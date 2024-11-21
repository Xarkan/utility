#define MSSQL
//#define MYSQL
//#define ORACLE

using System.Data.Common;

#if MSSQL
using System.Data.SqlClient;
#endif
#if MYSQL
using MySql.Data.MySqlClient;
#endif
#if ORACLE
using Oracle.ManagedDataAccess.Client;
#endif

namespace APPNAMESPACE.Services
{
    public enum DatabaseType { MySql, Oracle, MsSql }
    public enum DbConnectionName { Main }

    public abstract class Service
    {
        protected Database Db;
        protected Service(DbConnectionName connection = DbConnectionName.Main)
        {
            Db = new Database(connection);
        }
    }

    public class Database
    {
        public string ConnectionString;
        private readonly DatabaseType DbType;

        private DbConnection? Con;
        private DbTransaction? Transaction;

        public Database(DbConnectionName connection, string dbType = "mssql")
        {
            DbType = dbType switch {
                "mysql" => DatabaseType.MySql,
                "oracle" => DatabaseType.Oracle,
                "mssql" => DatabaseType.MsSql,
                _ => throw new NotImplementedException(),
            };
            string dbname = connection switch {
                _ => "Restauro",
            };
            IConfigurationRoot configuration = new ConfigurationBuilder().SetBasePath(Directory.GetCurrentDirectory()).AddJsonFile("appsettings.json", optional: true, reloadOnChange: true).Build();
            ConnectionString = configuration.GetValue<string>("ConnectionStrings:" + dbname) ?? "";
        }

        public void OpenTransaction()
        {
            Con = GetDbConnection(ConnectionString);
            Con.Open();
            Transaction = Con.BeginTransaction();
        }

        public List<Dictionary<string, object?>> Execute(string queryString, Dictionary<string, object?> binds)
        {
            Con = Transaction is not null ? Con : GetDbConnection(ConnectionString);
            DbCommand command = GetDbCommand(queryString, Con);
            foreach (var kv in binds)
                command.Parameters.Add(GetDbParameter(kv.Key, kv.Value ?? DBNull.Value));
            try {
                if (Transaction is null)
                    Con.Open();
                command.Transaction = Transaction;
                DbDataReader reader = command.ExecuteReader();
                bool doneOnce = false;
                List<string> fieldNames = new();
                List<Dictionary<string, object?>> rows = new();
                while (reader.Read()) {
                    Dictionary<string, object?> r = new();
                    for (int i = 0; i < reader.FieldCount; i++) {
                        if (!doneOnce) fieldNames.Add(reader.GetName(i));
                        var val = reader[i] is DBNull ? null : reader[i];
                        r.Add(fieldNames[i], val);
                    }
                    doneOnce = true;
                    rows.Add(r);
                }
                reader.Close();
                return rows;
            }
            catch (Exception ex) {
                RollBack();
                Console.WriteLine(ex);
                throw new Exception(ex.Message);
                return new List<Dictionary<string, object?>>();
            }
            finally { Close(); }
        }

        public int ExecuteNonQuery(string queryString, Dictionary<string, object?> binds)
        {
            Con = Transaction is not null ? Con : GetDbConnection(ConnectionString);
            DbCommand command = GetDbCommand(queryString, Con);
            foreach (var kv in binds)
                command.Parameters.Add(GetDbParameter(kv.Key, kv.Value ?? DBNull.Value));
            try {
                if (Transaction is null) Con.Open();
                command.Transaction = Transaction;
                return command.ExecuteNonQuery();
            }
            catch (Exception ex) {
                RollBack();
                Console.WriteLine(ex);
                throw new Exception(ex.Message);
                return 0;
            }
            finally { Close(); }
        }

        public void Commit()
        {
            if (Transaction is not null) {
                Transaction.Commit();
                Transaction.Dispose();
            }
            Transaction = null;
            if (Con is not null) {
                Con.Close();
                Con.Dispose();
            }
        }

        public void RollBack()
        {
            if (Transaction is not null) {
                Transaction.Rollback();
                Transaction.Dispose();
            }
            Transaction = null;
            if (Con is not null) {
                Con.Close();
                Con.Dispose();
            }
        }

        private void Close()
        {
            if (Transaction is null && Con is not null) {
                Con.Close();
                Con.Dispose();
            }
        }

        private DbConnection GetDbConnection(string conString)
        {
            return DbType switch {
#if MSSQL
                DatabaseType.MsSql => new SqlConnection(conString),
#elif MYSQL      
                DatabaseType.MySql => new MySqlConnection(conString),
#elif ORACLE
                DatabaseType.Oracle => new OracleConnection(conString),
#endif
                _ => throw new NotImplementedException(),
            };
        }

        private DbCommand GetDbCommand(string queryString, DbConnection connection)
        {
            return DbType switch {
#if MSSQL
                DatabaseType.MsSql => new SqlCommand(queryString, (SqlConnection)connection),
#elif MYSQL      
                DatabaseType.MySql => new MySqlCommand(queryString, (MySqlConnection)connection),
#elif ORACLE
                DatabaseType.Oracle => new OracleCommand(queryString, (OracleConnection)connection),
#endif
                _ => throw new NotImplementedException(),
            };
        }

        private DbParameter GetDbParameter(string key, object value)
        {
            return DbType switch {
#if MSSQL
                DatabaseType.MsSql => new SqlParameter("@" + key, value),
#elif MYSQL
                DatabaseType.MySql => new MySqlParameter("@" + key, value),
#elif ORACLE
                DatabaseType.Oracle => new OracleParameter(":" + key, value),
#endif
                _ => throw new NotImplementedException(),
            };
        }
    }
}
