/* (C) Sidi HAMADY */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>
#include <malloc.h>
#include <string.h>

#include "CZTS_Parameters.h"

/*
 * Electron SRH lifetime as a function of position
 * Statement: MATERIAL
 * Parameter: F.TAUN
 * Arguments:
 * x          location x (microns)
 * y          location y (microns)
 * temp       temperature (K)
 * nd         net concentration of donors (per cc)
 * na         net concentration of acceptors (per cc)
 * *taun      electron SRH lifetime (s)
 */
int taun(double x, double y, double temp, double nd, double na, double *taun)
{
    *taun = taun0_CZTS;

    return 0;
}

/*
 * Hole SRH lifetime as a function of position
 * Statement: MATERIAL
 * Parameter: F.TAUP
 * Arguments:
 * x          location x (microns)
 * y          location y (microns)
 * temp       temperature (K)
 * nd         net concentration of donors (per cc)
 * na         net concentration of acceptors (per cc)
 * *taup      hole SRH lifetime (s)
 */
int taup(double x, double y, double temp, double nd, double na, double *taup)
{
    *taup = taup0_CZTS;

    return 0;
}

/*
 * Radiative recombination rate as a function of composition and temperature.
 * Statement: MATERIAL
 * Parameter: F.COPT
 * Arguments:
 * temp       temperature (K)
 * xcomp      composition fraction x
 * ycomp      composition fraction y
 * *cop       radiative recomb. rate per cc per s
 */
int copt(double temp, double xcomp, double ycomp, double *cop)
{
    /* for x.comp = 0.2 */
    *cop = copt_CZTS;

    return 0;
}

/*
 * Electron Auger rate as a function of composition and temperature.
 * Statement: MATERIAL
 * Parameter: F.GAUN
 * Arguments:
 * temp       temperature (K)
 * xcomp      composition fraction x
 * ycomp      composition fraction y
 * *gan       elect. Auger recomb. rate (cm^6/s)
 */
int gaun(double temp, double xcomp, double ycomp, double *gan)
{
    *gan = augn_CZTS;

    return 0;
}

/*
 * Hole Auger rate as a function of composition and temperature.
 * Statement: MATERIAL
 * Parameter: F.GAUP
 * Arguments:
 * temp       temperature (K)
 * xcomp      composition fraction x
 * ycomp      composition fraction y
 * *gap       hole. Auger recomb. rate (cm^6/s)
 */
int gaup(double temp, double xcomp, double ycomp, double *gap)
{
    *gap = augp_CZTS;

    return 0;
}
