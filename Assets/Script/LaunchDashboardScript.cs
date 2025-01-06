using System;
using System.Diagnostics;
using UnityEngine;
using TMPro;


class Program: MonoBehaviour
{
    public TMP_InputField inputField;

    void Start()
    {

    }

    public void launchPythonScript()
    {
        String arg = inputField.text;

        // Chemin vers l'exécutable Python
        string pythonPath = @"python.exe";

        // Chemin vers le script Python
        string scriptPath = @"dashboard_plotly.py";

        // Arguments à passer au script Python
        string arguments = $"\"{scriptPath}\" {arg}";

        // Configuration du processus
        ProcessStartInfo psi = new ProcessStartInfo
        {
            FileName = pythonPath,
            Arguments = arguments,
            RedirectStandardOutput = false,
            RedirectStandardError = false,
            UseShellExecute = true,
            CreateNoWindow = false
        };

        // Lancement du processus
        Process process = new Process
        {
            StartInfo = psi
        };
        process.Start();
    }
}
