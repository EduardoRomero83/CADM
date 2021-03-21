#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <unistd.h>
#include <assert.h>
#include <sys/mman.h>
#include <sys/fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <time.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <sys/wait.h>

#define ERGMODE 0

/*
ERGMODE 0 - Measure total execution time (print in last line)
ERGMODE 1 - Report answers one on each line
ERGMODE 2 - Report individual response time per query and cluster
ERGMODE 3 - Report lookups per query
ERGMODE 4 - Other less-verbose debugging information
ERGMODE 5 - Other very verbose debugging information
ERGMODE 6 - Print hex of response lines for debugging
*/


#define MAXMSG  20000

#define SAMPLES 700
/* These two number need to come from argv.
* MAXFEAT should come directly from argv
* NUMBITS should be read from metadata.
* NUMBITS is the log base two of the smallest power of 2 greater than metadata/treeName.numpaths
* See definition of resultline for next change
*/
#define MAXFEAT 18
#define NUMBITS 16
#define NUMBYTES 3
#define NB 11
#define NUMCLASSES 7
#define PORT 7878
#define DICSPLIT 0
#define TABLESPLIT 0
#define CLUSTEROFFSET 0
#define TABLEOFFSET 0
#define TABLEUPPERLIMIT 16384


static __inline__ unsigned long long get_cycles(void)
{
  unsigned hi, lo;
  __asm__ __volatile__ ("rdtsc" : "=a"(lo), "=d"(hi));
  return ( (unsigned long long)lo)|( ((unsigned long long)hi)<<32 );
}

/* The size of the resultline array is the ceiling of
* ((metadata/treeName.bitsperaddline) at line 1) / 8
*/
typedef unsigned char resultline[NUMBYTES];

struct addLine {
  resultline rs;
  unsigned char signature;
};

struct decompressedAddLine {
  bool conf;
  unsigned char signature;
  int results[NUMCLASSES];
};

struct feature
{
  unsigned short int feat;
  unsigned short int val;
};

struct cluster
{
  //char ftcount;
  unsigned int signature;
  feature ft[MAXFEAT];
  unsigned int important;
  unsigned int common;
};


bool getRespline(unsigned int & address , unsigned int  *arrayAddr, unsigned int & signature);
unsigned int naiveoffset(unsigned int  sample, feature ft[], int cID);
void handleFailedHash(unsigned int & sequence, int cID, unsigned int prime, unsigned int k);
void hash(unsigned int & sequence, int cID, unsigned int prime1, unsigned int prime2);
void sumarrays(unsigned int arr1[], unsigned int arr2[]);
void handleConflict(unsigned int  & address, addLine* responses, int cID, unsigned int array[], unsigned int &  signature);
void getResp(unsigned int  *arrayAddr, int cID, unsigned int & address, addLine* responses, unsigned int &signature);
addLine *responses;
cluster *clusters;


// Driver function
__attribute__((optimize("unroll-loops")))
int main(int argc, char* argv[])
{
  if (argc != 2) {
    printf("This command takes 2 parameters: ./a.out treeName\n");
    printf("Max features is the maximum number of features in a cluster.\n");
    exit(-1);
  }
  int primes[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 183, 193, 197, 199,
211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293,
307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397,
401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499,
503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599,
601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691,
701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797,
809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887,
907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997};

  char treename[128];
  strcpy(treename,argv[1]);
  unsigned int cOffset = CLUSTEROFFSET;
  unsigned int tOffset = TABLEOFFSET;
  unsigned int tabUpper = TABLEUPPERLIMIT;
  tabUpper = tabUpper + tOffset;

  int sockfd, new_socket,fd;//connfd, fd, len;
  struct sockaddr_in servaddr, cli;
  int opt = 1;
  int addrlen = sizeof(cli);
  struct stat sb;
  struct timespec start_t, end_t, total_t;
  double ttime=0.0;
  int clusterFeatures=MAXFEAT;
  int port=PORT;//atoi(argv[2]);


  char featFile[512];
  strcpy(featFile,"./metadata/");
  strcat(featFile,treename);
  strcat(featFile,".features");
  char dicString[2];
  sprintf(dicString, "%d", DICSPLIT);//featFile = featFile + coreString;
  strcat(featFile,dicString);
  strcat(featFile,".bin");

  fd = open(featFile, O_RDONLY);
  if (fd < 0){
    printf("file does not exists %s\n", featFile);
    exit(-1);
  }

  fstat(fd, &sb);
  int clusterCount = (sb.st_size/(sizeof(cluster))) ;
  #if ERGMODE == 4
  printf("Are we aligned %d   --> %d  div %d\n",clusterCount, sb.st_size,sizeof(cluster));
  #endif

  clusters = (cluster*) mmap(NULL, sb.st_size, PROT_READ|PROT_WRITE, MAP_PRIVATE, fd, 0);
  if (clusters == MAP_FAILED) {
    printf ("memblock failed for clusters\n");
    exit(-1);
  }
  close(fd);



  // Test
  //printCluster(clusters[0]);
  //exit(0);
  char addFile[512];
  strcpy(addFile,"./metadata/");
  strcat(addFile,treename);
  strcat(addFile, ".addresses");
  char tabString[2];
  sprintf(tabString, "%d", TABLESPLIT);//addrFile = addrFile + coreString;
  strcat(addFile,tabString);
  strcat(addFile,".bin");

  fd = open(addFile, O_RDONLY);
  if (fd < 0){
    printf("file does not exists %s\n", addFile);
    exit(-1);
  }


  fstat(fd, &sb);
  //sb.st_size = 32000000;
  int responses_size =  sb.st_size;
  responses = (addLine*) mmap(NULL, sb.st_size, PROT_READ, MAP_SHARED, fd, 0);
  for (int prefetchCounter = 0; prefetchCounter < responses_size - 64; prefetchCounter += 64) {
    __builtin_prefetch(&(responses[prefetchCounter]),0,3);
  }
  if (responses == MAP_FAILED) {
    printf ("memblock failed for results\n");
    exit(-1);
  }
  close(fd);
  #if ERGMODE == 6
  for (int i = 0; i < NUMCLASSES; i++) {
    printf("Responses[%d] has rs: %x, %x and signature %x\n", i, responses[i].rs[0], responses[i].rs[1], responses[i].signature);
  }
  #endif

  // Listen on socket
  #if ERGMODE == 4
  printf("Listening on socket\n");
  fflush(stdout);
  #endif

  if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
    perror("socket failed");
    exit(EXIT_FAILURE);
  }

  if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
    perror("setsockopt");
    exit(EXIT_FAILURE);
  }
  servaddr.sin_family = AF_INET;
  servaddr.sin_addr.s_addr = inet_addr("127.0.0.1");
  servaddr.sin_port = htons(port);

  if (bind(sockfd, (struct sockaddr *)&servaddr, sizeof(servaddr))<0) {
    perror("bind failed");
    exit(EXIT_FAILURE);
  }
  if (listen(sockfd, 3) < 0)    {
    perror("listen");
    exit(EXIT_FAILURE);
  }

  if (( new_socket = accept(sockfd, (struct sockaddr *) &cli, (socklen_t*) &addrlen))<0) {
    perror("Accept");
    exit(EXIT_FAILURE);
  }

  int TEST_SIZE=SAMPLES*NB;
  unsigned char big_buffer[TEST_SIZE];
  unsigned char* buffer;
  unsigned int total_read = 0;
  int valread=0;
  #if ERGMODE == 4
  for (int t = 15; t < 20; t++){
      printf("clusterSign %d, common: %x, imp: %x \n", clusters[t].signature, clusters[t].common, clusters[t].important);
      for (int i = 0; i < MAXFEAT; i++) {
         printf("Feature: %d and value: %d \n", clusters[t].ft[i].feat, clusters[t].ft[i].val);
      }
      fflush(stdout);
  }
  #endif

  unsigned int pow2[MAXFEAT];
  for (int pow2Count = 0; pow2Count < clusterFeatures; pow2Count++) {
    pow2[(MAXFEAT - 1)-pow2Count] = (1<<((MAXFEAT - 1)-pow2Count));
  }


  cluster c1;
  for (int i = 0; i < clusterCount; i++) {
    __builtin_prefetch(clusters[i].ft,0,3);
    __builtin_prefetch(clusters[i].ft+64,0,3);
    for(int ftc = 0; ftc < clusterFeatures; ftc++) {
      clusters[i].ft[ftc].val = clusters[i].ft[ftc].val / 10;
    }
  }

    


  unsigned int O3Count = 0;
  while (total_read < TEST_SIZE) {
    #if ERGMODE == 4
    printf("Reading data from socket %d of size %d\n",new_socket, total_read);
    #endif
    if ((total_read + sizeof(char)*TEST_SIZE) > TEST_SIZE) {
      valread = read(new_socket, &(big_buffer[total_read]), TEST_SIZE - total_read);
    }
    else {
      valread = read(new_socket, &(big_buffer[total_read]), sizeof(char)*TEST_SIZE);
    }
    if (total_read == 0) {
      //#if ERGMODE == 0   // If you want time from first byte read
      //clock_gettime(CLOCK_MONOTONIC,&start_t);// = get_cycles();
      //#endif

    }
    if (valread > 0) {
      total_read += valread;
    }
  }

  #if ERGMODE == 5
  for (int l = 0; l < TEST_SIZE; l++)
    printf("%d \n", big_buffer[l]);
  #endif
  #if ERGMODE == 0  // If you want time from last byte read
  //printf("%d, %d \n", total_read, TEST_SIZE);
  //fflush(stdout);
  clock_gettime(CLOCK_MONOTONIC,&start_t);// = get_cycles();
  #endif
  #if ERGMODE == 4  // If you want time from last byte read
  printf("%d, %d \n", total_read, TEST_SIZE);
  #endif



  #if ERGMODE == 4
  printf("Forking processes");
  #endif

  int start=0;
int real_start = 0; //((start)*784);
int real_stop = TEST_SIZE;//(start+dist)*784;
unsigned int finalResps[NUMCLASSES] = {0,0,0,0,0,0,0};



#if ERGMODE == 4
printf("Starting to test and timings \n");
fflush(stdout);
#endif


for (int testX = real_start; testX < real_stop; testX=testX+(NB) ) {
  //printf("%d, %d, %d, %d \n", testX, real_start, real_stop, NB);
  //fflush(stdout);
  //if (testX != (real_start + 784 * 8)) {
     //continue;
  //}
  buffer=&(big_buffer[testX]);

  __builtin_prefetch(&(buffer[0]),0,3);
  __builtin_prefetch(&(buffer[64]),0,3);
  __builtin_prefetch(&(buffer[128]),0,3);
  __builtin_prefetch(&(buffer[192]),0,3);
  __builtin_prefetch(&(buffer[256]),0,3);
  __builtin_prefetch(&(buffer[320]),0,3);
  __builtin_prefetch(&buffer[384],0,3);
  __builtin_prefetch(&(buffer[448]),0,3);
  __builtin_prefetch(&(buffer[512]),0,3);
  __builtin_prefetch(&(buffer[576]),0,3);
  __builtin_prefetch(&(buffer[640]),0,3);
  __builtin_prefetch(&(buffer[704]),0,3);
  __builtin_prefetch(&(buffer[768]),0,3);
  

  for (int frc = 0; frc < NUMCLASSES; frc++) {
    finalResps[frc] = 0;
  }


  /*
  __builtin_prefetch(&(pow2),0,3);
  __builtin_prefetch(&(pow2[64]),0,3);
  __builtin_prefetch(&(pow2[128]),0,3);
  __builtin_prefetch(&(pow2[256]),0,3);
  __builtin_prefetch(&(pow2[320]),0,3);
  __builtin_prefetch(&(pow2[384]),0,3);
  */

  unsigned int uselessCount = 0;
  unsigned int vote = 0;


  for (unsigned int i = 0; i < clusterCount; i++) {

    struct timespec start_t2, end_t2;
    #if ERGMODE == 2
    clock_gettime(CLOCK_MONOTONIC,&start_t2);// = get_cycles();
    #endif

    unsigned int ftc = 0;
    unsigned int cfLoopBreak = 0;
    unsigned short wrapVar = 0;
    unsigned int shiftSize =0;
    unsigned short shiftSizeSet = 0;
    unsigned int lookup = 0;
    unsigned short last = 0;

    #if ERGMODE == 5
    printf("Cluster %d out of %d in test %d \n", i, clusterCount, testX/NB);
    #endif
    #if ERGMODE == 5
      printf("clusterSign %d, common: %x, imp: %x \n", clusters[i].signature, clusters[i].common, clusters[i].important);
      for (int j = 0; j < MAXFEAT; j++) {
         printf("Feature: %d and value: %d \n", clusters[i].ft[j].feat, clusters[i].ft[j].val);
      }
      fflush(stdout);
    #endif
    // 1.Load features and values.
    // 2.Execute clusterFeatures times or until both feat and val are 0
    // 3.Check if buffer[feat] <= val
    // 4.If 3 is true, add 1 in corresponding position at lookup. Else 0
    // 5.Break if currentFeature is important and does not match common at position 
    // 6.Update loop variables
    while( ((unsigned int)cfLoopBreak < clusterFeatures)  ) {
      // 1
      feature newFeat = clusters[i].ft[ftc];
      unsigned short c1ftfeat = newFeat.feat; //clusters[i].ft[ftc].feat;
      unsigned short c1ftval =  newFeat.val;;// clusters[i].ft[ftc].val;
      //unsigned short skip = 65535;//g1 0.5% y 2 seg
      #if ERGMODE == 5
	printf("%d, %d, %d -- ", c1ftfeat, buffer[c1ftfeat], c1ftval);
      #endif
      // 2
      //skip += ((c1ftfeat + c1ftval) != 0);// g1 0.5% y 2 seg
      if (((c1ftfeat + c1ftval) == 0) && (cfLoopBreak > 0)) {
	break;
      }
      //3
      unsigned short hit = (buffer[c1ftfeat] <= c1ftval);
      //4
      shiftSize= (clusterFeatures - 1-ftc);
      unsigned short x = 0;
      unsigned int currFeat = ((x - (hit)) & pow2[shiftSize]);
      lookup = lookup| currFeat;
      //5
      bool needCheck = pow2[shiftSize] & clusters[i].important;
      unsigned int match = currFeat & clusters[i].important;
      unsigned int match2 = pow2[shiftSize] & clusters[i].common;
      unsigned short lateSkip = 65535;
      lateSkip += ((!needCheck) || (match == match2));
      cfLoopBreak += lateSkip;
      //6
      ftc++;
      cfLoopBreak++;
      //cfLoopBreak += skip;// grupo 1. 0.5% y 2 seg mas
      //
      //
      //
      // Old code did not work. 10%ish penalty. It is fast
      /*unsigned short hit = 65535 + (buffer[c1ftfeat] > c1ftval);
      //shiftSize= (clusterFeatures - 1-ftc);
      //shiftSizeSet = shiftSizeSet | hit;
      bool shiftseed = ( (hit & (c1ftfeat + c1ftval)) > 0);//   * pow2[shiftSize];
      cfLoopBreak =  (unsigned int)(cfLoopBreak + (unsigned short)(wrapVar - ((c1ftfeat == 0) & (c1ftval == 0))));
      unsigned int x = 0;
      x = (x - shiftseed)&pow2[clusterFeatures-1-ftc];
      lookup=lookup|x;*/
      #if ERGMODE == 5
	printf("%x, %x == ", currFeat, lookup);
      #endif
      /*
      cfLoopBreak++;
      ftc++;
      unsigned short skip = 65535 + ((((pow2[clusterFeatures-1-ftc]&(clusters[i].important) ) > 0) && ((x !=(clusters[i].common & pow2[clusterFeatures-1-ftc])))) || ((pow2[clusterFeatures-1-ftc]&(clusters[i].important)) == 0));
      cfLoopBreak = cfLoopBreak|skip;
*/
    }
#if ERGMODE == 5
printf("\n");
#endif

unsigned int worthit= 0;
worthit = lookup & clusters[i].important;

#if ERGMODE == 5
printf("cid: %d, clusterSign %d, lookup: %x, common: %x, imp: %x \n", i, clusters[i].signature, worthit, clusters[i].common, clusters[i].important);
#endif


 if ( (worthit== clusters[i].common)) {

  #if ERGMODE == 5
  printf("Made a lookup\n");
  #endif
  unsigned char signature = 0;
  unsigned int tempResps[NUMCLASSES] = {0,0,0,0,0,0,0};
  vote = 100000;

  // CHristopher Stewart -- This looks like deadcode
  shiftSize= (clusterFeatures -ftc);
  unsigned int base = 373+373 * (i + cOffset);
  unsigned int ending = base % (1 << (clusterFeatures - ftc +1 )); //pow2[shiftSize]; //
  lookup = lookup | ending;

  hash(lookup, i + cOffset, 2, 23);
  bool conf = false;
  if ((lookup > tOffset) || lookup >= tabUpper) {
    continue;
  }
  lookup -= tOffset;
  conf = responses[lookup].rs[0] >> 7;
  signature = responses[lookup].signature;
  //#if ERGMODE == 5
  //printf("Conflict: %d, signature: %d\n",conf, signature);
  //#endif
  // First lookup does not have a conflict. Get vote and done
  if ( ( (conf == false) )  &&  (signature == clusters[i].signature)) {
    int i = 0;
    int currentByte = 0;
    int currentBit = 1;
    vote = responses[lookup].rs[2];
    //#if ERGMODE == 5
    //printf("Responses[%d] = %x, %x, %x\n", lookup, responses[lookup].rs[0],responses[lookup].rs[1],responses[lookup].rs[2]);
    //#endif

    uselessCount++;

  } // if sig matches
  // First lookup has conflict. Handle it and check if there is a new conflict.
  else if ((conf == true)  ) {
    continue; //Conflict matching turned off
    // Christopher Stewart - November 2019
    // The code below replicates the code above but gets only 2 array elements
    // Needed for Eduardo's Handle Conflict functions
    int i = 0;
    int currentByte = 0;
    int currentBit = 1;
    bool hash1 = responses[lookup].rs[0] & 1;
    int p1 = primes[responses[lookup].rs[1]];
    int p2 = primes[responses[lookup].rs[2]];
    if (!hash1) {
      hash(lookup, i, p1, p2);
    }
    else {
      handleFailedHash(lookup, i, p1, p2);
    }
    //Conflict handled. Check if new conflict exists on new lookup
    conf = responses[lookup].rs[0] >> 7;
    signature = responses[lookup].signature;

    // No new conflict. Get vote and done
    if ( (conf == false)  &&  (signature == clusters[i].signature)) {
      // Christopher Stewart - November 2019
      // The code below is tricky decrompression implemented by Eduardo Romero Gainza
      int i = 0;
      int currentByte = 0;
      int currentBit = 1;
      vote = responses[lookup].rs[2];
      //End of inlined decompress -- CS
    //#if ERGMODE == 5
    //printf("After Conflict-- Conflict: %d, signature: %d\n",conf, signature);
    //printf("Responses[%d] = %x, %x, %x\n", lookup, responses[lookup].rs[0],responses[lookup].rs[1],responses[lookup].rs[2]);
    //#endif


      uselessCount++;
      //for (int ithree = 0; ithree < 10; ithree++) { -- Original version
      //printf ("%d , ", tempResps[ithree]);
      //finalResps[ithree] = finalResps[ithree] + tempResps[ithree];
      //}

    } // if sig matches
    // Second conflict exists. Handle it
    else if ((conf == true)  ) {


      // Christopher Stewart - November 2019
      // The code below replicates the code above but gets only 2 array elements
      // Needed for Eduardo's Handle Conflict functions
      int i = 0;
      int currentByte = 0;
      int currentBit = 1;
      bool hash1 = responses[lookup].rs[0] & 1;
      int p1 = primes[responses[lookup].rs[1]];
      int p2 = primes[responses[lookup].rs[2]];
      if (!hash1) {
        hash(lookup, i, p1, p2);
      }
      else {
        handleFailedHash(lookup, i, p1, p2);
      }
      // Conflicts handled.

      // Get response from new lookup after two handled conflicts
      vote = responses[lookup].rs[2];
      uselessCount++;
    //#if ERGMODE == 5
    //printf("After Second Conflict-- Conflict: %d, signature: %d\n",conf, signature);
    //printf("Responses[%d] = %x, %x, %x\n", lookup, responses[lookup].rs[0],responses[lookup].rs[1],responses[lookup].rs[2]);
    //#endif
    }

    //for (int ithree = 0; ithree < 10; ithree++) { -- Original version
    //printf ("%d , ", tempResps[ithree]);
    //finalResps[ithree] = finalResps[ithree] + tempResps[ithree];
    //}

    //HERE	  finalResps[max] = finalResps[max] + 1;
  }
  if (vote < NUMCLASSES) {
    finalResps[vote]++;
  }
 } // if worthit

#if ERGMODE == 2
clock_gettime(CLOCK_MONOTONIC,&end_t2);// = get_cycles();
if (1 ==1) {
  double ttime =0;
  ttime = (ttime + (end_t2.tv_nsec - start_t2.tv_nsec)) * 1e-9;
  if (ttime < 0.000001) {
    printf("Decrompress: %0.9f CiD: %d Lookup: %d Worthit: %d  FTC: %d\n", ttime, i, lookup, (worthit == clusters[i].common), ftc  );
  }
  else {
    O3Count++;
  }
}
#endif




} // cluster sweep
//printf("%d \n", testX);
#if ERGMODE == 1
for(int i2=0; i2 < NUMCLASSES; i2++) {
  printf("%d, ", finalResps[i2]);
}
printf("\n");
fflush(stdout);
#endif
#if ERGMODE == 3
printf("Lookups: %d \n", uselessCount);
#endif


#if ERGMODE == 2
 printf("Below: %d",O3Count);
#endif

}


#if ERGMODE == 0
clock_gettime(CLOCK_MONOTONIC,&end_t);
  ttime = 0;
  ttime = (end_t.tv_sec - start_t.tv_sec) * 1e9;
  ttime = (ttime + (end_t.tv_nsec - start_t.tv_nsec)) * 1e-9;
  printf("Total: %f\n", ttime  );
  printf("a: %d \n", finalResps[5] );
#endif
close(sockfd);
exit(0);
}





inline void getResp(unsigned int *array, int cID, unsigned int & address, addLine* responses, unsigned int &  signature) {
  hash(address, cID, 2, 23);
  if (!(getRespline(address, array, signature))) {
    return;
  }
  else {
    handleConflict(address, responses, cID, array, signature);
  }

}

inline bool getRespline(unsigned int & address, unsigned int  *arrayMain, unsigned int & signature) {
  addLine resps;
  unsigned int array[10] = {0,0,0,0,0,0,0,0,0,0};
  memcpy((void*)&resps, (void*)&(responses[address]), sizeof(addLine));

  bool conf = resps.rs[0] >> 7;
  signature = resps.signature;


  int i = 0;
  int currentByte = 0;
  int currentBit = 1;
  while(i < 10) {
    // Case: Bit is 0 so number in array is 0
    if (!(((resps.rs[currentByte] << currentBit) >> 7) & 1)) {

      //printf(" Bit is 0 Current bit is %d \n", currentBit);
      currentBit++;
      // Start on next byte
      if (currentBit > 7) {
        currentByte++;
        currentBit -= 8;
      }
      array[i] = 0;
      i++;
    }
    // Bit is 1 and the next bit is in this byte
    else if (currentBit < 7) {


      //printf(" Not 0 Current bit is %d \n", currentBit);
      currentBit++;
      // Number starts with 10 so we need to read 5 bits
      if (!(((resps.rs[currentByte] << currentBit) >> 7) & 1)) {

        // printf(" Number starts with 10:  %d \n", currentBit);
        // Number is in the same byte
        if (currentBit < 3) {
          unsigned int n = resps.rs[currentByte] >> (2 - currentBit);
          n = n & 0x1F;
          array[i] = n;
          //printf("Read 5 bits of same byte and number is %d \n", n);
          i++;
          currentBit += 6;
          if (currentBit > 7) {
            currentByte++;
            currentBit -= 8;
          }

        }
        // Number is partially on next byte
        else if (currentBit < 7) {
          int infirst = 7 - currentBit;
          unsigned int n = resps.rs[currentByte] << (currentBit + 25);
          n = n >> 27;
          unsigned int n2 = resps.rs[currentByte + 1] >> (infirst + 3);
          n = n | n2;
          array[i] = n;
          //printf("Read 5 bits split into two bytes and number is %d \n", n);
          i++;
          currentByte++;
          currentBit -= 2; // Add the 6 bits read but subtract
        }
        // Number is entirely in next byte
        else {
          currentByte++;
          unsigned int n = resps.rs[currentByte] >> 3;
          array[i] = n;
          //printf("Read 5 bits in next byte and number is %d \n", n);
          i++;
          currentBit = 5;
        }
      }
      // Number starts with 11 so we need to read 13 bits
      else {
        //printf("Starts with 11 and currentBit is %d \n,", currentBit);
        // The beginning of the 13 bits is in this byte
        if (currentBit < 7) {
          int inByte = 7 - currentBit;
          unsigned int p1 = resps.rs[currentByte] << (32- inByte);
          unsigned int p2, p3 = 0;
          p1 = p1 >> 19;
          // We need the entire next byte + some of the one after that
          if (inByte < 5) {
            p2 = resps.rs[currentByte + 1] << (5 - inByte);
            p3 = resps.rs[currentByte + 2] >> (3 + inByte);
          }
          // We need the entire next byte
          else if (inByte == 5) {
            p2 = resps.rs[currentByte + 1];
          }
          // Need less than 8 bits from next byte
          else {
            p2 = resps.rs[currentByte + 1] >> (inByte - 5);
          }
          unsigned int n = (p1 | p2) | p3;
          array[i] = n;
          i++;
          currentBit += 14;
          while (currentBit > 7) {
            currentBit -= 8;
            currentByte++;
          }
        }
        // Read next byte plus 5 bits
        else{
          unsigned int p1 = resps.rs[currentByte + 1] << 5;
          unsigned int p2 = resps.rs[currentByte + 2] >> 3;
          unsigned int n = p1 | p2;
          array[i] = n;
          i++;
          currentByte += 2;
          currentBit = 5;
        }
      }

    }
    // The bit is 1 and the next bit is in the next byte
    else {

      currentByte++;
      // The next bit is 0 so we read 5 bits
      if (!(resps.rs[currentByte] >> 7)) {
        unsigned int n = (resps.rs[currentByte] & 0x7F) >> 2;
        array[i] = n;
        i++;
        currentBit = 6;
      }
      // The next bit is a 1, so we read the 7 bits of the new byte + 6 of another one
      else {
        unsigned int p1 = (resps.rs[currentByte] & 0x7F) << 6;
        unsigned int p2 = resps.rs[currentByte + 1] >> 2;
        array[i] = p1 | p2;
        i++;
        currentByte++;
        currentBit = 6;
      }
    }
  }
  /*for (int loop=0; loop<10;loop++) {
  printf("%d,",array[loop]);
}
printf("\n");
fflush(stdout);*/


memcpy(arrayMain,array,sizeof(int)*10);
return conf;
}

void sumarrays(unsigned int arr1[], unsigned int arr2[]) {
  for (int i = 0; i < NUMCLASSES; i++) {
    arr1[i] += arr2[i];
  }
}

inline void handleConflict(unsigned int &  address, addLine* responses, int cID, unsigned int array[], unsigned int &  signature) {
  if (array[1] != 0) {
    hash(address, cID, array[0], array[1]);
  }
  else {
    handleFailedHash(address, cID, array[0], array[2]);
  }
  /*printf("Handle COnflict Address: %d\n",address);
  fflush(stdout);*/

  //printf("%x  %d   ",address, cID);
  if (!getRespline(address, array, signature)) {
    return;
  }
  else {
    handleConflict(address, responses, cID, array, signature);
  }

  /*printf("after respLine lookup 2nd\n");
  fflush(stdout);*/

}

inline void hash(unsigned int & sequence, int cID, unsigned int prime1, unsigned int prime2) {
  sequence = ((unsigned int) ((prime1 * sequence) + (prime2 * cID))  ) % (1 << NUMBITS);
}

inline void handleFailedHash(unsigned int & sequence, int cID, unsigned int prime, unsigned int k) {
  sequence = ( (unsigned int) ((sequence + k + cID) * prime)) % (1 << NUMBITS);
}

