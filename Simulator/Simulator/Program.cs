// See https://aka.ms/new-console-template for more information

using System.Diagnostics;
using Simulator;

string path = "D:\\Diploma\\dataset";

DirectoryInfo di = new DirectoryInfo(path);
foreach (DirectoryInfo dir in di.GetDirectories()) dir.Delete(true); 

Generator.StartGenerator();
    
List<Task> tasks = new List<Task>();
for (int i = 0; i < 10; i++)
{
    Machine machine = new Machine(i);
    tasks.Add(Task.Run(() => machine.Start(path))); 
}

Task.WaitAll(tasks.ToArray());