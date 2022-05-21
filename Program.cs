using System.Text;

var filename = args.FirstOrDefault();

if (string.IsNullOrEmpty(filename))
{
    throw new ArgumentNullException(nameof(filename));
}

var file = File.OpenRead(filename);
var reader = new BinaryReader(file);

// check file magic
if (reader.ReadUInt32() != 22038099 /* SFP<1> */)
{
    throw new ArgumentException("File is not a game.pack: Invalid magic");
}

var numFiles = reader.ReadUInt32();

// check file length
if (reader.ReadUInt32() != file.Length)
{
    throw new ArgumentException("File is not a valid game.pack: Invalid length");
}

for (var i = 0; i < numFiles; i++)
{
    // skip past sf::BasicString members, not needed
    file.Position += 8;

    var name = GetString(reader.ReadBytes(112));
    var size = reader.ReadUInt32();
    var offset = reader.ReadUInt32();

    Console.WriteLine($"Name = {name}, Size = {size}, Offset = {offset}");

    // extract file
    ExtractFile(name, offset, size);
}

// null terminates the array and returns it as string
// could be left out if we read size from sf::BasicString
string GetString(byte[] str)
{
    return Encoding.ASCII.GetString(
        str.Take(Array.FindIndex(str, x => x == 0)).ToArray());
}

void ExtractFile(string name, uint offset, uint size)
{
    // save the current position
    var current = file.Position;

    file.Position = offset;
    var data = reader.ReadBytes((int)size);

    var path = Path.Join("export", name);

    Directory.CreateDirectory(Path.GetDirectoryName(path));
    File.WriteAllBytes(path, data);

    // restore cursor
    file.Position = current;
}
