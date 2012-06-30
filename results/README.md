/*
 * INNER_LOOPs
 *  1 is approx twice fast as 1
 *  3 seems a little faster than 2
 *
 *  5 x 2 MB
 *  --------
 *   1pf   135 sec
 *   2pf   160
 *   3pf   160
 *
 *  5 x 4 MB
 *  --------
 *   1pf  257 sec
 *   2pf  315 
 *   3pf  335
 *
 *  5 x 8 MB
 *  --------
 *   1pf  505 sec
 *   2pf  675 
 *   3pf  660
*
 *  5 x 20 MB
 *  --------
 *   1pf 1195 sec
 *   2pf 1784   
 *   3pf 1618  
 * 
 *  10 x 2 MB
 *  --------
 *   1    150 sec 
 *   2     36
 *   3     35   
 *
 *  5 x 20 MB
 *  --------
 *   1    1295   
 *   2    320  860 sec 
 *   3    296
 *   3pf  231  800   (pre-filter == check for match of last n chars)
 */