import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
from urllib.parse import urljoin
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import xml.etree.ElementTree as ET
import os



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

# Streaming asset path
streaming_asset_path = "Assets/StreamingAssets/"

# Store session data
launched_data = []
completed_data = []

# Function to process the LRS response
def process_lrs_response(response_json, data_store):
    statements = response_json.get("statements", [])
    data_store.extend(statements)

    # Check for pagination
    more_url = response_json.get("more", None)
    if more_url:
        print("Fetching more data...")
        full_more_url = urljoin(LRS_ENDPOINT, more_url)
        more_response = requests.get(
            full_more_url,
            auth=HTTPBasicAuth(LRS_USERNAME, LRS_PASSWORD),
            headers=headers
        )
        if more_response.status_code == 200:
            process_lrs_response(more_response.json(), data_store)
        else:
            print(f"Error fetching more data: {more_response.status_code} - {more_response.text}")

# Fetch data based on a specific verb
def fetch_data(verb):
    query_params = {
    "agent": json.dumps({
        "account": {
            "homePage": "https://www.lip6.fr/mocah/",
            "name":"3D37C851"
        }
    }),
    # check vocabulary lrs
    "verb": verb
    #"limit": 100
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
    
# Subplots
def plot_with_subplots(levels, max_scores, min_scores, avg_execution_times, max_execution_times, min_execution_times, level_scores, cpt_lunched):
    # Create a figure with two side-by-side subplots
    fig = make_subplots(
        rows=2, cols=2,  # 1 row, 2 columns for side-by-side layout
        subplot_titles=("Max and Min Scores Per Level (Divided by the level max score)", 
                        "Execution Times Per Level", 
                        "Scores Distribution Per Level",
                        "Number of launched per level"
                        ),  
        horizontal_spacing=0.2,  # Increase spacing between the two plots
        vertical_spacing= 0.3 # Increase spacing between the two plots
    )

    # Left subplot: Scores
    fig.add_trace(
        go.Bar(x=levels, y=max_scores, name='Max Score', marker_color='skyblue', showlegend=False),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=levels, y=min_scores, name='Min Score', marker_color='orange', showlegend=False),
        row=1, col=1
    )

    # Right subplot: Execution Times
    fig.add_trace(
        go.Bar(x=levels, y=avg_execution_times, name='Avg Execution Time (s)', marker_color='lightgreen', showlegend=False),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(x=levels, y=max_execution_times, name='Max Execution Time (s)', marker_color='orange', showlegend=False),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(x=levels, y=min_execution_times, name='Min Execution Time (s)', marker_color='blue', showlegend=False),
        row=1, col=2
    )

    # Bottom left subplot: Violine scores plot
    for level, scores in level_scores.items():
        fig.add_trace(
            go.Box(y=scores, name=level, boxmean=True, showlegend=False),
            row=2, col=1
        )

    # Bottom right subplot: Number of launched per level
    fig.add_trace(
        go.Bar(x=list(cpt_lunched.keys()), y=list(cpt_lunched.values()), name='Number of launched', marker_color='orange', showlegend=False),
        row=2, col=2
    )

    # Add borders around each graph
    fig.add_shape(
        type="rect",
        xref="paper", yref="paper",  # Use paper coordinates for layout-level shapes
        x0=0.0, x1=0.4, y0=0.015, y1=0.35,  # Left graph border
        line=dict(color="white", width=2)  # Border color and width
    )
    fig.add_shape(
        type="rect",
        xref="paper", yref="paper",  # Use paper coordinates for layout-level shapes
        x0=0.6, x1=1.0, y0=0, y1=0.35,  # Right graph border
        line=dict(color="white", width=2)  # Border color and width
    )

    fig.add_shape(
        type="rect",
        xref="paper", yref="paper",  # Use paper coordinates for layout-level shapes
        x0=0.0, x1=0.4, y0=0.65, y1=1,  # Left graph border
        line=dict(color="white", width=2)  # Border color and width
    )
    fig.add_shape(
        type="rect",
        xref="paper", yref="paper",  # Use paper coordinates for layout-level shapes
        x0=0.6, x1=1.0, y0=0.65, y1=1,  # Right graph border
        line=dict(color="white", width=2)  # Border color and width
    )

    # Update axis titles
    fig.update_xaxes(title_text="Level Name", row=1, col=1)
    fig.update_yaxes(title_text="Scores", row=1, col=1)

    fig.update_xaxes(title_text="Level Name", row=1, col=2)
    fig.update_yaxes(title_text="Execution Times (s)", row=1, col=2)

    fig.update_xaxes(title_text="Level Name", row=2, col=1)
    fig.update_yaxes(title_text="Scores", row=2, col=1)

    fig.update_xaxes(title_text="Level Name", row=2, col=2)
    fig.update_yaxes(title_text="Number of launched levels", row=2, col=2)

    # Layout adjustments
    fig.update_layout(
        title='SPY Dashboard',
        #title='Scores and Execution Times Per Level',
        title_y=0.99,
        title_x=0.5,
        # Title font size
        title_font_size=24,
        barmode='group',
        template='plotly_dark',
        # height=1000,  # Adjust height for better visualization
        # width=1920,  # Set width for full-screen visualization
        margin=dict(t=80, b=50, l=20, r=20),  # Margins
    )

    # Ensure bars take up space effectively
    fig.update_layout(
        bargap=0.1,  # Adjust spacing between bars
        bargroupgap=0.12  # Adjust spacing between groups
    )

    fig.add_annotation(
        x=0.43, y=1.0, text="<span style='color:skyblue'>■</span> Max Score<br><span style='color:orange'>■</span> Min Score",
        showarrow=False, xref="paper", yref="paper", align="left",
        font=dict(size=12)
    )

    # Légende pour la deuxième sous-figure
    fig.add_annotation(
        x=1.07, y=1.0, text="<span style='color:lightgreen'>■</span> Avg Exec Time<br><span style='color:orange'>■</span> Max Exec Time<br><span style='color:blue'>■</span> Min Exec Time",
        showarrow=False, xref="paper", yref="paper", align="left",
        font=dict(size=12)
    )

    # Show the figure
    fig.show()

def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    scores = []
    for child in root:
        if child.tag == 'score':
            scores.append(child.attrib)
    return scores

def main():

    print("Fetching launched data...")
    launched_response = fetch_data("http://adlnet.gov/expapi/verbs/launched")
    if launched_response:
        process_lrs_response(launched_response, launched_data)

    print("Fetching completed data...")
    completed_response = fetch_data("http://adlnet.gov/expapi/verbs/completed")
    if completed_response:
        process_lrs_response(completed_response, completed_data)

    for d in launched_data:
        d['timestamp'] = d['timestamp'][0:-2]+"Z"
        d['timestamp'] = d['timestamp'].replace("Z", "+00:00")
    for d in completed_data:
        d['timestamp'] = d['timestamp'][0:-2]+"Z"
        d['timestamp'] = d['timestamp'].replace("Z", "+00:00")

    # Sort data by timestamp
    launched_data.sort(key=lambda x: datetime.fromisoformat(x['timestamp'].replace("Z", "+00:00")))
    completed_data.sort(key=lambda x: datetime.fromisoformat(x['timestamp'].replace("Z", "+00:00")))

    # Match completed with the closest launched before it
    level_scores = {}
    level_execution_times = {}
    cpt_lunched = {}
    for completed in completed_data:
        completed_timestamp = datetime.fromisoformat(completed['timestamp'].replace("Z", "+00:00"))
        
        # Extraire le score si disponible
        extensions = completed['result'].get('extensions', {})
        score_list = extensions.get('https://spy.lip6.fr/xapi/extensions/score', [])
        if score_list:
            completed_score = int(score_list[0])
        else:
            completed_score = 0

        # Trouver le dernier launched avant ce completed
        matching_launched = None
        for launched in reversed(launched_data):
            launched_timestamp = datetime.fromisoformat(launched['timestamp'].replace("Z", "+00:00"))
            if launched_timestamp <= completed_timestamp:
                matching_launched = launched

                break
        
        
        if matching_launched:
            # Extraire le nom du niveau
            level_name = matching_launched['object']['definition']['extensions']['https://spy.lip6.fr/xapi/extensions/value'][0]
            level_xml_path = streaming_asset_path + level_name

            # Incrémentation du nombre de lancement
            if level_name not in cpt_lunched:
                cpt_lunched[level_name] = 0
            cpt_lunched[level_name] += 1
            
            stars_scores = parse_xml(level_xml_path)[0]
            max_score = int(stars_scores['threeStars'])
            # Ajouter le score au niveau correspondant
            if level_name not in level_scores:
                level_scores[level_name] = []
            level_scores[level_name].append(completed_score/max_score)


            # Calculer le temps d'exécution
            execution_time = (completed_timestamp - launched_timestamp).total_seconds()

            # Ajouter le temps d'exécution au niveau correspondant
            if level_name not in level_execution_times:
                level_execution_times[level_name] = []
            level_execution_times[level_name].append(execution_time)

    # Calculer les scores max et min pour chaque niveau
    levels = list(level_scores.keys())
    max_scores = [max(scores) if scores else 0 for scores in level_scores.values()]
    min_scores = [min(scores) if scores else 0 for scores in level_scores.values()]

    levels = list(level_execution_times.keys())
    avg_execution_times = [sum(times) / len(times) if times else 0 for times in level_execution_times.values()]
    max_execution_times = [max(times) if times else 0 for times in level_execution_times.values()]
    min_execution_times = [min(times) if times else 0 for times in level_execution_times.values()]

    plot_with_subplots(levels, max_scores, min_scores, avg_execution_times, max_execution_times, min_execution_times, level_scores, cpt_lunched)



if __name__ == "__main__":
    main()

