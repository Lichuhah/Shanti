namespace Simulator;

public static class MacGenerator
{
    private static char[] _chars = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','F'];
    private static Random rnd = new Random(DateTime.Now.Microsecond);
    
    public static string GenerateMac()
    {
        string mac = String.Empty;
        mac += _chars[rnd.Next(14)];
        mac += _chars[rnd.Next(14)];
        mac += ':';
        mac += _chars[rnd.Next(14)];
        mac += _chars[rnd.Next(14)];
        mac += ':';
        mac += _chars[rnd.Next(14)];
        mac += _chars[rnd.Next(14)];
        mac += ':';
        mac += _chars[rnd.Next(14)];
        mac += _chars[rnd.Next(14)];
        mac += ':';
        mac += _chars[rnd.Next(14)];
        mac += _chars[rnd.Next(14)];
        mac += ':';
        mac += _chars[rnd.Next(14)];
        mac += _chars[rnd.Next(14)];
        return mac;
    }
}