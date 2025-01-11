from dash import Dash, dcc, html, Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
from urllib.parse import urljoin
import webbrowser
import xml.etree.ElementTree as ET

all_session_names = []
all_session_data = {}
launched_responses = {}
completed_responses = {}
executed_responses = {}
scenarios_dropdown = ["All"]

# LRS Configuration
LRS_ENDPOINT = "https://lrsels.lip6.fr/data/xAPI"
LRS_USERNAME = "9fe9fa9a494f2b34b3cf355dcf20219d7be35b14"
LRS_PASSWORD = "b547a66817be9c2dbad2a5f583e704397c9db809"
XAPI_VERSION = "1.0.3"

# Headers
headers = {
    "X-Experience-API-Version": XAPI_VERSION,
    "Content-Type": "application/json"
}

streaming_asset_path = "Assets/StreamingAssets/"

# Fetch data based on a specific verb
def fetch_data(verb, session_name):
    query_params = {
        "agent": json.dumps({
            "account": {
                "homePage": "https://www.lip6.fr/mocah/",
                "name": session_name
            }
        }),
        "verb": verb
    }

    response = requests.get(
        f"{LRS_ENDPOINT}/statements",
        auth=HTTPBasicAuth(LRS_USERNAME, LRS_PASSWORD),
        params=query_params,
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to query LRS: {response.status_code} - {response.text}")
        return None

# Function to process LRS response
def process_lrs_response(response_json, data_store):
    statements = response_json.get("statements", [])
    data_store.extend(statements)

    # Check for pagination
    more_url = response_json.get("more", None)
    if more_url:
        full_more_url = urljoin(LRS_ENDPOINT, more_url)
        more_response = requests.get(
            full_more_url,
            auth=HTTPBasicAuth(LRS_USERNAME, LRS_PASSWORD),
            headers=headers
        )
        if more_response.status_code == 200:
            process_lrs_response(more_response.json(), data_store)

def parse_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        scores = []
        for child in root:
            if child.tag == 'score':
                scores.append(child.attrib)
        return scores
    except Exception as e:
        print(f"Error parsing {xml_file}: {e}")
        return []

def format_level_name(level_name, scenario_dropdown):
    level_name = level_name.replace(".xml","")
    parts = level_name.split('/')
    if scenario_dropdown == "All" or scenario_dropdown is None:
        return '/'.join(parts[1:])
    else:
        return parts[-1]

# Generate subplots
def generate_subplots(levels, max_scores, min_scores, avg_execution_times, max_execution_times, min_execution_times, level_scores, cpt_launched):

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Max and Min Scores Per Level (Divided by the level max score)", 
                        "Execution Times Per Level", 
                        "Scores Distribution Per Level",
                        "Number of Execution Per Level"),
        horizontal_spacing=0.2,
        vertical_spacing=0.3
    )

    # Max and Min Scores
    fig.add_trace(go.Bar(x=levels, y=max_scores, name='Max Score', marker_color='skyblue', legendgroup="min_max_scores"), row=1, col=1)
    fig.add_trace(go.Bar(x=levels, y=min_scores, name='Min Score', marker_color='lightpink', legendgroup="min_max_scores"), row=1, col=1)

    # Execution Times
    fig.add_trace(go.Bar(x=levels, y=avg_execution_times, name='Avg Execution Time (s)', marker_color='lightgreen', legendgroup="execution_times"), row=1, col=2)
    fig.add_trace(go.Bar(x=levels, y=max_execution_times, name='Max Execution Time (s)', marker_color='orange', legendgroup="execution_times"), row=1, col=2)
    fig.add_trace(go.Bar(x=levels, y=min_execution_times, name='Min Execution Time (s)', marker_color='blue', legendgroup="execution_times"), row=1, col=2)

    # Scores Distribution
    for level, scores in level_scores.items():
        fig.add_trace(go.Box(y=scores, name=level, boxmean=True, showlegend=False), row=2, col=1)

    # Number of Launched Levels
    fig.add_trace(go.Bar(x=list(cpt_launched.keys()), y=list(cpt_launched.values()), name='Number of Launched', marker_color='darkred', legendgroup="launch_counts"), row=2, col=2)

    fig.update_layout(
        template="plotly_dark",
        barmode='group',
        bargap=0.1,
        margin=dict(t=80, b=50, l=20, r=20),
    )
    return fig

# Initialize Dash App
app = Dash(__name__)

default_figure = {
    "data": [],
    "layout": {
        "plot_bgcolor": "black",
        "paper_bgcolor": "black",
        "xaxis": {"visible": False},
        "yaxis": {"visible": False},
        "font": {"color": "white"},
        "annotations": [
            {
                "text": "No data available",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 20, "color": "white"},
                "x": 0.5,
                "y": 0.5,
                "xanchor": "center",
                "yanchor": "middle",
            }
        ],
    },
}

app.layout = html.Div([
    html.H1("SPY Dashboard", style={"text-align": "center", "color": "white"}),

    # Section pour saisir les noms des sessions
    html.Div([
        html.Label("Enter session codes (comma-separated):", style = {"color": "white", "margin-left": "10px"}),
        dcc.Input(id="session-names", type="text", placeholder="Enter session names...", style={"width": "200px", "margin-left": "10px"}),
        html.Button("Submit", id="submit-button", n_clicks=0, style={"margin-left": "10px"}),
    ], style={"display":"flex", "align-items": "center", "justify-content":"center", "text-align": "center", "margin-bottom": "10px"}),

    # Section pour sélectionner un scénario
    html.Div([
        html.Label("Select a scenario:", style = {"color": "white", "margin-left": "10px"}),
        dcc.Dropdown(
            id="scenario-dropdown",
            options=["All"],
            placeholder="Select a scenario...",
            style={"width": "200px", "margin-left": "10px", "margin-right": "10px"}
        ),
        html.Button("Actualize", id="actualize-button", n_clicks=0, style={"margin-left": "10px"}),
    ], style={"display":"flex", "align-items": "center", "justify-content":"center", "text-align": "center", "margin-bottom": "10px"}),

    # Graphique du tableau de bord
    dcc.Graph(id="dashboard-graph", figure = default_figure, style={"height": "80vh", "width": "98%", "margin-left": "10px", "margin-right": "10px", "margin-bottom": "10px"}),
])

@app.callback(
    Output("dashboard-graph", "figure"),
    Input("submit-button", "n_clicks"),
    State("session-names", "value"),
    Input("scenario-dropdown", "value"),
)

def update_dashboard(n_clicks, session_names, scenario_dropdown):
    global all_session_names
    global all_session_data
    global launched_responses
    global completed_responses
    global executed_responses
    global scenarios_dropdown

    if not session_names:
        return default_figure

    session_names = [name.strip() for name in session_names.split(",")]
    for session_name in session_names:

        if session_name in all_session_data.keys():
            continue

        launched_data = []
        completed_data = []
        executed_data = []

        launched_response = fetch_data("http://adlnet.gov/expapi/verbs/launched", session_name)
        completed_response = fetch_data("http://adlnet.gov/expapi/verbs/completed", session_name)
        executed_response = fetch_data("https://spy.lip6.fr/xapi/verbs/executed", session_name)

        if launched_response:
            process_lrs_response(launched_response, launched_data)
        if completed_response:
            process_lrs_response(completed_response, completed_data)
        if executed_response:
            process_lrs_response(executed_response, executed_data)

        for d in launched_data:
            d['timestamp'] = d['timestamp'][0:-2] + "Z"
            d['timestamp'] = d['timestamp'].replace("Z", "+00:00")
        for d in completed_data:
            d['timestamp'] = d['timestamp'][0:-2] + "Z"
            d['timestamp'] = d['timestamp'].replace("Z", "+00:00")
        for d in executed_data:
            d['timestamp'] = d['timestamp'][0:-2] + "Z"
            d['timestamp'] = d['timestamp'].replace("Z", "+00:00")

        launched_data.sort(key=lambda x: datetime.fromisoformat(x['timestamp'].replace("Z", "+00:00")))
        completed_data.sort(key=lambda x: datetime.fromisoformat(x['timestamp'].replace("Z", "+00:00")))
        executed_data.sort(key=lambda x: datetime.fromisoformat(x['timestamp'].replace("Z", "+00:00")))

        # Analyser les données pour cette session
        level_scores = {}
        level_execution_times = {}
        scenarios = {}
        cpt_launched = {}
        cpt_executed = {}
        for launched in launched_data:
            launched_timestamp = datetime.fromisoformat(launched['timestamp'].replace("Z", "+00:00"))
            matching_executed = next(
                (l for l in executed_data
                 if datetime.fromisoformat(l['timestamp'].replace("Z", "+00:00")) >= launched_timestamp),
                None
            )
            if matching_executed:
                level_name = launched['object']['definition']['extensions']['https://spy.lip6.fr/xapi/extensions/value'][0]
                if level_name not in cpt_executed:
                    cpt_executed[level_name] = 0
                cpt_executed[level_name] += 1

                scenario = launched['object']['definition']['extensions']['https://spy.lip6.fr/xapi/extensions/context'][0]
                if scenario not in scenarios_dropdown:
                    scenarios_dropdown.append(scenario)
                if level_name not in scenarios:
                    scenarios[level_name] = scenario

        for completed in completed_data:
            completed_timestamp = datetime.fromisoformat(completed['timestamp'].replace("Z", "+00:00"))
            
            # Extraire le score si disponible
            extensions = completed['result'].get('extensions', {})
            score_list = extensions.get('https://spy.lip6.fr/xapi/extensions/score', [])
            completed_score = int(score_list[0]) if score_list else 0

            # Trouver le dernier launched avant ce completed
            matching_launched = next(
                (l for l in reversed(launched_data)
                 if datetime.fromisoformat(l['timestamp'].replace("Z", "+00:00")) <= completed_timestamp),
                None
            )
            
            if matching_launched:
                level_name = matching_launched['object']['definition']['extensions']['https://spy.lip6.fr/xapi/extensions/value'][0]
                level_xml_path = streaming_asset_path + level_name

                # Incrémentation du nombre de lancement
                if level_name not in cpt_launched:
                    cpt_launched[level_name] = 0
                cpt_launched[level_name] += 1
                
                stars_scores = parse_xml(level_xml_path)
                if not stars_scores:
                    print(f"Error parsing {level_xml_path}")
                    continue
                stars_scores = stars_scores[0]
                max_score = int(stars_scores['threeStars'])

                # Ajouter le score au niveau correspondant
                if level_name not in level_scores:
                    level_scores[level_name] = []
                level_scores[level_name].append(completed_score / max_score)

                # Calculer le temps d'exécution
                execution_time = (completed_timestamp - datetime.fromisoformat(matching_launched['timestamp'].replace("Z", "+00:00"))).total_seconds()
                if level_name not in level_execution_times:
                    level_execution_times[level_name] = []
                level_execution_times[level_name].append(execution_time)

        levels = list(level_scores.keys())
        #print(levels)
        max_scores = [max(scores) if scores else 0 for scores in level_scores.values()]
        min_scores = [min(scores) if scores else 0 for scores in level_scores.values()]

        # for level, max_score in zip(levels, max_scores):
        #     print(f"Niveau: {level} - Score Max: {max_score}")

        # for level, min_score in zip(levels, min_scores):
        #     print(f"Niveau: {level} - Score Min: {min_score}")

        avg_execution_times = [sum(times) / len(times) if times else 0 for times in level_execution_times.values()]
        max_execution_times = [max(times) if times else 0 for times in level_execution_times.values()]
        min_execution_times = [min(times) if times else 0 for times in level_execution_times.values()]

        all_session_data[session_name] = {
            "levels": levels,
            "max_scores": max_scores,
            "min_scores": min_scores,
            "avg_execution_times": avg_execution_times,
            "max_execution_times": max_execution_times,
            "min_execution_times": min_execution_times,
            "level_scores": level_scores,
            "cpt_launched": cpt_executed,
            "scenarios" : scenarios
        }

    combined_data = {}
    all_levels = set().union(*[data["levels"] for session_name, data in all_session_data.items() if session_name in session_names])
    if scenario_dropdown != None and scenario_dropdown != "All":
        all_levels = {level for level in all_levels if any(data["scenarios"].get(level) == scenario_dropdown for data in all_session_data.values())}

    for level in all_levels:
        combined_data[level] = {
            "max_score": [],
            "min_score": [],
            "avg_execution_time": [],
            "max_execution_time": [],
            "min_execution_time": [],
            "scores": [],
            "launch_counts": [],
        }
        for session_name, data in all_session_data.items():
            if session_name in session_names:
                if level in data["levels"]:
                    idx = data["levels"].index(level)
                    combined_data[level]["max_score"].append(data["max_scores"][idx])
                    combined_data[level]["min_score"].append(data["min_scores"][idx])
                    combined_data[level]["avg_execution_time"].append(data["avg_execution_times"][idx])
                    combined_data[level]["max_execution_time"].append(data["max_execution_times"][idx])
                    combined_data[level]["min_execution_time"].append(data["min_execution_times"][idx])
                    combined_data[level]["scores"].extend(data["level_scores"][level])
                    combined_data[level]["launch_counts"].append(data["cpt_launched"].get(level, 0))

    if len(session_names) > 1 or True:
        # Trier les niveaux par ordre alphabétique
        levels = sorted(combined_data.keys())
        # Réorganiser les données dans le même ordre
        sorted_combined_data = {level: combined_data[level] for level in levels}

        max_scores = [sum(data["max_score"]) / len(data["max_score"]) for data in sorted_combined_data.values()]
        min_scores = [sum(data["min_score"]) / len(data["min_score"]) for data in sorted_combined_data.values()]
        avg_execution_times = [sum(data["avg_execution_time"]) / len(data["avg_execution_time"]) for data in sorted_combined_data.values()]
        max_execution_times = [sum(data["max_execution_time"]) / len(data["max_execution_time"]) for data in sorted_combined_data.values()]
        min_execution_times = [sum(data["min_execution_time"]) / len(data["min_execution_time"]) for data in sorted_combined_data.values()]
        cpt_executed = [sum(data["launch_counts"]) / len(data["launch_counts"]) for data in sorted_combined_data.values()]
        level_scores = {level: data["scores"] for level, data in sorted_combined_data.items()}

    levels = [format_level_name(level, scenario_dropdown) for level in levels]
    level_scores = {format_level_name(level, scenario_dropdown): scores for level, scores in level_scores.items()}
    return generate_subplots(levels, max_scores, min_scores, avg_execution_times, max_execution_times, min_execution_times, level_scores, dict(zip(levels, cpt_executed)))

@app.callback(
    Output("scenario-dropdown", "options"),
    Input("actualize-button", "n_clicks"),
)
def update_scenario_dropdown(n_clicks):
    if not scenarios_dropdown:
        return []
    return [{"label": name, "value": name} for name in scenarios_dropdown]

if __name__ == "__main__":
    port = 8050
    webbrowser.open(f"http://127.0.0.1:{port}")
    app.run_server(debug=False, port = port)
