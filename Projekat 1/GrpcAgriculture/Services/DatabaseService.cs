using MongoDB.Driver;

namespace GrpcAgriculture.Services;

public class DatabaseService
{
  private readonly IMongoDatabase _database;

  public DatabaseService(IConfiguration config)
  {
    var connectionString = config["MongoDb:ConnectionString"];
    var databaseName = config["MongoDb:DatabaseName"];

    var client = new MongoClient(connectionString);
    _database = client.GetDatabase(databaseName);
  }

  public IMongoCollection<T> GetCollection<T>(string name)
  {
    return _database.GetCollection<T>(name);
  }
}