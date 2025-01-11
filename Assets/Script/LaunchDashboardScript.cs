using System;
using System.Diagnostics;
using UnityEngine;
using TMPro;


class Program: MonoBehaviour
{

    void Start()
    {

    }

    public void launchPythonScript()
    {

        // Chemin vers l'exécutable Python
        string pythonPath = @"python.exe";

        // Chemin vers le script Python
        string scriptPath = @"test.py";

        // Arguments à passer au script Python
        string arguments = $"\"{scriptPath}\"";

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
