import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Statement;

class SqlQueries {
    void unsafeQueries(Connection connection, String userId) throws SQLException {
        Statement statement = connection.createStatement();

        // ruleid: bugledger-sql-injection-java
        statement.executeQuery("SELECT * FROM users WHERE id = " + userId);

        // ruleid: bugledger-sql-injection-java
        statement.executeUpdate("DELETE FROM users WHERE id = " + userId);

        // ruleid: bugledger-sql-injection-java
        statement.execute("UPDATE users SET active = 1 WHERE id = " + userId);
    }

    void safeQueries(Connection connection, String userId) throws SQLException {
        // ok: bugledger-sql-injection-java
        PreparedStatement statement =
                connection.prepareStatement("SELECT * FROM users WHERE id = ?");
        statement.setString(1, userId);
        statement.executeQuery();

        Statement fixedStatement = connection.createStatement();
        // ok: bugledger-sql-injection-java
        fixedStatement.executeQuery("SELECT * FROM users");
    }
}
