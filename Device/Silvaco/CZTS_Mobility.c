/* (C) Sidi HAMADY */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>
#include <malloc.h>
#include <string.h>

#include "CZTS_Parameters.h"

/*
 * Composition, temperature and doping dependent electron mobility
 * Statement: MATERIAL
 * Parameter: F.CONMUN
 * Arguments:
 * xcomp      composition fraction x
 * ycomp      composition fraction y
 * temp       temperature (K)
 * nd         net concentration of donors (per cc)
 * na         net concentration of acceptors (per cc)
 * x          location x (microns)
 * y          location y (microns)
 * taun       electron SRH lifetime (s)
 * *mun       electron mobility
 */
int conmun(double xcomp, double ycomp, double temp, double nd, double na, double x, double y, double taun, double *mun)
{
    double tempa_CZTS = 1.0;
    double tempb_CZTS = 1.0;
    double tempc_CZTS = 1.0;
    double tempd_CZTS = 1.0;

    double tempa = pow(temp / 300.0, tempa_CZTS);
    double tempb = pow(temp / 300.0, tempb_CZTS);
    double tempc = pow(temp / 300.0, tempc_CZTS);
    double tempd = pow(temp / 300.0, tempd_CZTS);
    double Ntotal = nd + na;

    *mun = (mu1n_CZTS * tempa) + (((mu2n_CZTS * tempb) - (mu1n_CZTS * tempa)) / (1.0 + pow(Ntotal / (ncritn_CZTS * tempc), deltan_CZTS * tempd)));

    return 0;
}

/*
 * Composition, temperature and doping dependent hole mobility
 * Statement: MATERIAL
 * Parameter: F.CONMUP
 * Arguments:
 * xcomp      composition fraction x
 * ycomp      composition fraction y
 * temp       temperature (K)
 * nd         net concentration of donors (per cc)
 * na         net concentration of acceptors (per cc)
 * x          location x (microns)
 * y          location y (microns)
 * taup       hole SRH lifetime (s)
 * *mup       hole mobility
 */
int conmup(double xcomp, double ycomp, double temp, double nd, double na, double x, double y, double taup, double *mup)
{
    /* mobility for x.comp = 0.2 */

    double tempa_CZTS = 1.0;
    double tempb_CZTS = 1.0;
    double tempc_CZTS = 1.0;
    double tempd_CZTS = 1.0;

    double tempa = pow(temp / 300.0, tempa_CZTS);
    double tempb = pow(temp / 300.0, tempb_CZTS);
    double tempc = pow(temp / 300.0, tempc_CZTS);
    double tempd = pow(temp / 300.0, tempd_CZTS);
    double Ntotal = nd + na;

    *mup = (mu1p_CZTS * tempa) + (((mu2p_CZTS * tempb) - (mu1p_CZTS * tempa)) / (1.0 + pow(Ntotal / (ncritp_CZTS * tempc), deltap_CZTS * tempd)));

    return 0;
}

