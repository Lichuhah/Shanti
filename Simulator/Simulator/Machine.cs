using System.Globalization;
using System.Text.Json;

namespace Simulator;

public class Machine
{
    private string mac = MacGenerator.GenerateMac();
    private int index = 0;
    public Machine(int index)
    {
        this.index = index;
    }
    
    public void Start(string path)
    {
        string fullPath = path + "\\" + index;
        int fCount = Directory.GetFiles(fullPath, "*", SearchOption.TopDirectoryOnly).Length - 1;
        for (int i = 0; i < fCount; i++)
        {
            IEnumerable<string> lines = File.ReadLines($"{fullPath}\\{i}.csv");
            foreach (var line in lines.Skip(1))
            {
                string[] row = line.Split('\t');
                Row data = new Row()
                {
                    TimeStamp = DateTime.Parse(row[0]),
                    AmbientTemperature = Convert.ToDouble(row[1], CultureInfo.InvariantCulture),
                    AmbientPressure = Convert.ToDouble(row[2], CultureInfo.InvariantCulture),
                    Speed = Convert.ToDouble(row[3], CultureInfo.InvariantCulture),
                    Temperature = Convert.ToDouble(row[4], CultureInfo.InvariantCulture),
                    Pressure = Convert.ToDouble(row[5], CultureInfo.InvariantCulture),
                    Vibration = Convert.ToDouble(row[6], CultureInfo.InvariantCulture),
                };
                Console.WriteLine($"[{this.mac}] {JsonSerializer.Serialize(data)}");
            }
        }
       
    }
}