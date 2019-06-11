// ======================================================================================================
// SLALOM - Open-Source Solar Cell Multivariate Optimizer
// Copyright(C) 2012-2019 Sidi OULD SAAD HAMADY (1,2,*), Nicolas FRESSENGEAS (1,2). All rights reserved.
// (1) Université de Lorraine, Laboratoire Matériaux Optiques, Photonique et Systèmes, Metz, F-57070, France
// (2) Laboratoire Matériaux Optiques, Photonique et Systèmes, CentraleSupélec, Université Paris-Saclay, Metz, F-57070, France
// (*) sidi.hamady@univ-lorraine.fr
// SLALOM source code is available to download from:
// https://github.com/sidihamady/SLALOM
// https://hal.archives-ouvertes.fr/hal-01897934
// http ://www.hamady.org/photovoltaics/slalom_source.zip
// Cite as: S Ould Saad Hamady and N Fressengeas, EPJ Photovoltaics, 9:13, 2018.
// See Copyright Notice in COPYRIGHT
// ======================================================================================================

// ------------------------------------------------------------------------------------------------------
// File:      InN_GaN_Parameters.h
// Type:      C header
// Purpose:   InN and GaN parameters used by all C modules
// Can be adapted for other compound semiconductors
// ------------------------------------------------------------------------------------------------------

#ifndef InN_GaN_PARAMETERS_H
#define InN_GaN_PARAMETERS_H

#define BowingBandgap           1.43
#define BowingAffinity          0.8

/* Bandgap and density of states parameters */
/* InN (parameters taken from: http://www.ioffe.ru/SVA/NSM/Semicond/InN/) */
#define eg300_InN               0.7
#define egalpha_InN             0.914e-3
#define egbeta_InN              825.0
#define nc300_InN               9.1e17
#define nv300_InN               5.3e19
#define permittivity_InN        15.3
#define affinity_InN            5.6

#define vsatn_InN               1.3e7
#define betanField_InN          1.0
#define vsatp_InN               1.7e7
#define betapField_InN          2.0

/* Recombination parameters */
#define augn_InN                1.5e-30
#define augp_InN                1.5e-30
#define copt_InN                2.0e-10
/* taun0 from Appl. Phys. Lett. 71 (18) 1997 */
#define taun0_InN               1.0e-9
#define taup0_InN               1.0e-9

#define e31_InN                -0.33
#define e33_InN                 0.65
#define psp_InN                -0.042
#define arichn_InN              27.4
#define arichp_InN              31.1
#define mzz_InN                 0.21
#define mtt_InN                 0.20
#define a1_InN                 -7.21
#define a2_InN                 -0.44
#define a3_InN                  6.68
#define a4_InN                 -3.46
#define a5_InN                 -3.40
#define a6_InN                 -4.90
#define ev0_InN                -2.64
#define d1_InN                  0.014
#define d2_InN                  0.019
#define a0_InN                  3.189

/* Caughey-Thomas mobility parameters */
/* G.F. Brown et al., Solar Energy Materials and Solar Cells 94 (2010) 83, 478 */
#define mu1n_InN                30.0
#define mu2n_InN                1100.0
#define deltan_InN              1.0
#define ncritn_InN              8e18
#define mu1p_InN                3.0
#define mu2p_InN                340.0
#define deltap_InN              2.0
#define ncritp_InN              3e17

/* Bandgap and density of states parameters */
/* GaN (ref.: http://www.ioffe.ru/SVA/NSM/Semicond/GaN/) */
#define eg300_GaN               3.42
#define egalpha_GaN             9.47e-4
#define egbeta_GaN              621.0
#define nc300_GaN               2.3e18
#define nv300_GaN               4.6e19
#define permittivity_GaN        8.9
#define affinity_GaN            4.1

#define vsatn_GaN               1.3e7
#define betanField_GaN          1.0
#define vsatp_GaN               1.7e7
#define betapField_GaN          2.0

/* Recombination parameters */
#define augn_GaN                1.5e-30
#define augp_GaN                1.5e-30
#define copt_GaN                1.1e-8
#define taun0_GaN               1.0e-9
#define taup0_GaN               1.0e-9

#define e31_GaN                -0.33
#define e33_GaN                 0.65
#define psp_GaN                -0.034
#define arichn_GaN              27.4
#define arichp_GaN              31.1
#define mzz_GaN                 0.21
#define mtt_GaN                 0.20
#define a1_GaN                 -7.21
#define a2_GaN                 -0.44
#define a3_GaN                  6.68
#define a4_GaN                 -3.46
#define a5_GaN                 -3.40
#define a6_GaN                 -4.90
#define ev0_GaN                -2.64
#define d1_GaN                  0.014
#define d2_GaN                  0.019
#define a0_GaN                  3.189

/* Caughey-Thomas mobility parameters */
/* G.F. Brown et al., Solar Energy Materials and Solar Cells 94 (2010) 83, 478 */
#define mu1n_GaN                55.0
#define mu2n_GaN                1000.0
#define deltan_GaN              1.0
#define ncritn_GaN              2e17
#define mu1p_GaN                3.0
#define mu2p_GaN                170.0
#define deltap_GaN              2.0
#define ncritp_GaN              3e17

#endif