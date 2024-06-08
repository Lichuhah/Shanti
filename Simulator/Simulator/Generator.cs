using System.Diagnostics;

namespace Simulator;

public static class Generator
{
    public static void StartGenerator()
    {
        using Process dataGenerate = new Process();
        dataGenerate.StartInfo = new ProcessStartInfo
        {
            FileName = "cmd.exe",
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            RedirectStandardInput = true,
            Arguments = "/c " + "python script.py",
            CreateNoWindow = true,
            WorkingDirectory = "../../../../",
        };
        dataGenerate.OutputDataReceived += (a,b) => Console.WriteLine(b.Data);
        dataGenerate.Start();
        dataGenerate.BeginOutputReadLine();
        dataGenerate.WaitForExit();
    }
}