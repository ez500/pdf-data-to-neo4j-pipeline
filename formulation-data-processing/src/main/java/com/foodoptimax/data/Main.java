package com.foodoptimax.data;

import org.neo4j.driver.*;

/**
 * Establishes a connection with the local Neo4j server.
 *
 * @author Eugene Zhang
 * @version 1.0-ALPHA, Oct 6, 2025
 * 
 */
public class Main {
    public static void main(String[] args) {
        Driver driver = GraphDatabase.driver("localhost:7474", AuthTokens.basic("neo4j", "neo4j"));
        driver.verifyConnectivity();
        // Use driver to interact with database..
        driver.close();
    }
}
