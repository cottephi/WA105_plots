#include <mysql/mysql.h>
#include <mysql/mysqld_error.h>

#include <time.h>
#include <stdlib.h>
#include <stdio.h>

/*********************************************************
 * char * WA105db_getversion()
 * Return the version of the current library
 * ******************************************************/
extern char * WA105db_getversion();

/*********************************************************
 * MYSQL * WA105db_connect(void)
 * Do the connection to the db 
 * sent a error in the stderr if the connection is bad 
 * Reurn a pointer to the mysql database
 * ******************************************************/
extern MYSQL * WA105db_connect(void);

/*********************************************************
 * WA105db_disconnect(MYSQL *db);
 * Close the database
 * db : pointer to the database
 * ******************************************************/
extern void WA105db_disconnect(MYSQL *db);

// ======================================================
double getSensorValue(const char * name, time_t time);


