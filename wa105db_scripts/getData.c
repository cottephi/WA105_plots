#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <signal.h>

#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <stdbool.h>

#include <time.h>
#include "wa105db.h"

#define C_MAX_NB_PARAM 300

typedef struct ParamType
{
  char  name[20];
  int   nbValue;
  int   * date;
  float * value;
}tParamType;

tParamType  paramsList[C_MAX_NB_PARAM];


float findFirstValue(int startdate,int iParam)
{
  float v;
  char cmd[500];
  MYSQL_ROW *row;
  MYSQL_RES *res ;
  MYSQL * db =  WA105db_connect();

  sprintf(cmd, "select * from %s where date<=%d order by date desc limit 0,1;", paramsList[iParam].name,startdate);
  mysql_query(db,cmd);
  res = mysql_store_result(db);
  while( row = mysql_fetch_row(res) )
  {
        v=atof(row[1]);
  }

  mysql_free_result(res);
  WA105db_disconnect(db);
  return v;
}


void doit(int startdate,int enddate, int nbParams, int sampling)
{
  int i;
  char cmd[500];
  MYSQL_ROW *row;
  MYSQL_RES *res ;
  MYSQL * db =  WA105db_connect();

  for (i=0;i<nbParams;i++)
  {
    sprintf(cmd, "select * from %s where date>%d and date<%d;", paramsList[i].name,startdate,enddate);
    mysql_query(db,cmd);
    res = mysql_store_result(db);
    paramsList[i].nbValue = mysql_num_rows(res)/sampling;
    paramsList[i].date = (int*) malloc (paramsList[i].nbValue * sizeof(int));
    paramsList[i].value = (float *) malloc (paramsList[i].nbValue * sizeof(int));
//    fprintf(stderr,"%s : %d values sampling level:%d\r\n",paramsList[i].name ,paramsList[i].nbValue,sampling);
    int v=0;
    int current=0;
    int s=1;
    while( row = mysql_fetch_row(res) )  
    {
        if (s >= sampling)
        {
           s=1;
           paramsList[i].date[current]=atoi(row[0]);
           paramsList[i].value[current]=atof(row[1]);
           current++;
        }
        else s++;
        v++;
    }
  }
  mysql_free_result(res);
  WA105db_disconnect(db);
}

#define C_DEFAULT_VALUE 12345678.

void showData(int startdate,int enddate,int nbParams)
{
  int i,j;
  int d,p;

  float value[C_MAX_NB_PARAM],lastvalue[C_MAX_NB_PARAM];
  int  sdate;
  bool toShow;

  printf("date\t");
  for (p=0;p<nbParams;p++)
  {
    printf("%s\t",paramsList[p].name);
  }
  printf("\r\n");
  for (i=0;i<C_MAX_NB_PARAM;i++) lastvalue[i]=C_DEFAULT_VALUE;
  for (d=startdate;d<enddate;d++)
  {
    toShow=false;
    for (i=0;i<C_MAX_NB_PARAM;i++) value[i]=C_DEFAULT_VALUE;
    sdate=0;
    for (p=0;p<nbParams;p++)
    {
       for (i=0;i<paramsList[p].nbValue;i++)
       {
          if (d==(int) paramsList[p].date[i]) 
          {
            toShow=true;
            sdate= d;
            value[p]= paramsList[p].value[i];
            lastvalue[p]=value[p];
          }
          else if ((d==startdate) && (lastvalue[p]==C_DEFAULT_VALUE))
               {
                  toShow=true;
                  sdate= d;
                  value[p]= findFirstValue(startdate,p);
                  lastvalue[p]=value[p];
                }
                else 
                {
                  sdate= d;
                  value[p]= lastvalue[p];
                }
       }
    }

    if (toShow)
    {
      printf("%d\t",sdate);
      for (p=0;p<nbParams;p++)
      {
         if (value[p]==12345678.) printf("\t");
         else printf("%5.5f\t",value[p]);
      }
      printf("\r\n");
    }

  }
}

void usage(char *name)
{
  printf("%s -s <start date> -e <end date> [-r 1|..|n ] Parms1 [Params2  Params3 .... ParamsN]\n\r",name);
  printf("start date: Timestamp\n\r");
  printf("End   date: Timestamp\n\r");
  printf("-r <resolution ( 1:full  to n:divide/n ) \n\r");
  printf("ex: ./getData -r 10 -s 1488304800 -e 1488305400  TE0073 TE0074 \r\n");
}

int main(int argc, char *argv[])
{
           int flags, opt;
           int nsecs, tfnd;
           int startdate,enddate;
           int sampling=1;

           nsecs = 0;
           tfnd = 0;
           flags = 0;
           while ((opt = getopt(argc, argv, "r:s:e:")) != -1) 
           {
               switch (opt) {
               case 's':
                   startdate = atoi(optarg);
                   break;
               case 'e':
                   enddate = atoi(optarg);
                   break;
               case 'r':
                   sampling = atoi(optarg);
                   if (sampling<=0) sampling=1;
                   break;
               default: /* '?' */
                   usage(argv[0]);
                   exit(EXIT_FAILURE);
               }
           }
          if (optind < argc) 
          {
               int i=0;
               while (optind < argc)
                   strcpy(paramsList[i++].name, argv[optind++]);

               doit(startdate,enddate,i, sampling);
               showData(startdate,enddate,i);
          }
          else
          usage(argv[0]); 

          exit(EXIT_SUCCESS);
}

