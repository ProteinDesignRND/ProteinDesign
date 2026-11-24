import * as THREE from 'three';

export interface SidechainAtom {
  name: string;
  element: 'C' | 'N' | 'O' | 'S';
  pos: [number, number, number];
}

export interface SidechainBond {
  from: [number, number, number];
  to: [number, number, number];
  elementFrom: 'C' | 'N' | 'O' | 'S';
  elementTo: 'C' | 'N' | 'O' | 'S';
}

export interface HydrogenBond {
  donor: [number, number, number];
  acceptor: [number, number, number];
  donorLabel: string;
  acceptorLabel: string;
}

export interface PdbResidue {
  resSeq: number;
  resName: string;
  chain: string; // 'A' (Target) or 'B' (Binder)
  ca: [number, number, number]; // [x, y, z] in Angstroms
  sec: 'helix' | 'sheet' | 'loop';
  defaultPlddt: number;
  isHotspot?: boolean;
  isMutated?: boolean;
}

export interface MacromolecularStructureData {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  targetId: string;
  isComplex: boolean;
  chainA: {
    name: string;
    protein: string;
    description: string;
    residuesCount: number;
    color: number;
  };
  chainB?: {
    name: string;
    protein: string;
    description: string;
    residuesCount: number;
    color: number;
    designRegions: string;
  };
  residues: PdbResidue[];
  interfaceBonds: SidechainBond[];
  interfaceAtoms: SidechainAtom[];
  hydrogenBonds: HydrogenBond[];
}

export const centerCoordinates = (residues: PdbResidue[]): PdbResidue[] => {
  if (residues.length === 0) return [];
  let sumX = 0, sumY = 0, sumZ = 0;
  residues.forEach((r) => {
    sumX += r.ca[0];
    sumY += r.ca[1];
    sumZ += r.ca[2];
  });
  const cX = sumX / residues.length;
  const cY = sumY / residues.length;
  const cZ = sumZ / residues.length;
  return residues.map((r) => ({
    ...r,
    ca: [
      parseFloat((r.ca[0] - cX).toFixed(2)),
      parseFloat((r.ca[1] - cY).toFixed(2)),
      parseFloat((r.ca[2] - cZ).toFixed(2)),
    ],
  }));
};

// ---------------------------------------------------------------------------
// 1. AUTHENTIC 1UBQ UBIQUITIN COORDINATES (PDB 1UBQ, 1.80 Å)
// ---------------------------------------------------------------------------
export const UBIQUITIN_1UBQ_COORDS: PdbResidue[] = [
  {
    "resSeq": 1,
    "resName": "MET",
    "chain": "A",
    "ca": [
      26.27,
      25.41,
      2.84
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 2,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      26.85,
      29.02,
      3.9
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 3,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      26.23,
      30.06,
      7.5
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 4,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      26.77,
      33.44,
      9.2
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 5,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      28.61,
      33.97,
      12.5
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 6,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      27.69,
      37.31,
      14.14
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 7,
    "resName": "THR",
    "chain": "A",
    "ca": [
      30.23,
      38.64,
      16.66
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 8,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      29.61,
      41.18,
      19.47
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 9,
    "resName": "THR",
    "chain": "A",
    "ca": [
      31.42,
      43.94,
      17.55
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 10,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      28.98,
      43.96,
      14.68
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 11,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      31.19,
      42.01,
      12.33
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 12,
    "resName": "THR",
    "chain": "A",
    "ca": [
      29.54,
      39.02,
      10.65
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 13,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      31.72,
      36.29,
      9.18
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 14,
    "resName": "THR",
    "chain": "A",
    "ca": [
      30.5,
      33.88,
      6.51
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 15,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      31.68,
      30.27,
      6.64
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 16,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      31.22,
      27.34,
      4.28
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 17,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      30.29,
      24.25,
      6.19
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 18,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      28.47,
      20.94,
      5.98
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 19,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      25.83,
      19.82,
      8.49
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 20,
    "resName": "SER",
    "chain": "A",
    "ca": [
      28.05,
      16.84,
      9.21
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 21,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      30.8,
      19.08,
      10.57
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 22,
    "resName": "THR",
    "chain": "A",
    "ca": [
      31.4,
      19.06,
      14.29
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 23,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      31.29,
      22.2,
      16.42
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 24,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      35.03,
      21.72,
      17.07
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 25,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      35.59,
      21.95,
      13.3
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 26,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      33.53,
      25.1,
      12.98
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 27,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      35.6,
      26.71,
      15.74
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 28,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      38.79,
      25.76,
      13.88
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 29,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      37.47,
      27.39,
      10.67
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 30,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      36.73,
      30.57,
      12.64
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 31,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      40.27,
      30.51,
      14.12
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 32,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      41.72,
      30.02,
      10.64
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 33,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      39.81,
      32.99,
      9.23
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 34,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      39.68,
      35.55,
      12.07
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 35,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      42.34,
      34.27,
      14.43
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 36,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      40.23,
      33.72,
      17.51
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 37,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      41.46,
      30.75,
      19.59
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 38,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      38.82,
      28.02,
      19.89
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 39,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      39.06,
      28.06,
      23.7
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 40,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      37.74,
      31.64,
      23.71
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 41,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      34.74,
      30.88,
      21.47
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 42,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      31.2,
      30.33,
      22.78
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 43,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      28.76,
      29.57,
      19.91
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 44,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      25.03,
      30.17,
      20.4
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 45,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      22.13,
      29.06,
      18.18
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 46,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      18.44,
      29.14,
      19.08
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 47,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      19.4,
      29.89,
      22.66
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 48,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      21.55,
      26.8,
      23.13
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 49,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      25.35,
      26.87,
      23.64
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 50,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      26.83,
      24.52,
      21.01
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 51,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      29.02,
      21.66,
      22.29
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 52,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      32.26,
      20.67,
      20.51
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 53,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      31.57,
      16.96,
      19.82
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 54,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      28.11,
      17.44,
      18.28
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 55,
    "resName": "THR",
    "chain": "A",
    "ca": [
      27.57,
      18.19,
      14.56
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 56,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      25.59,
      21.11,
      13.07
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 57,
    "resName": "SER",
    "chain": "A",
    "ca": [
      22.92,
      18.58,
      12.03
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 58,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      22.42,
      17.64,
      15.69
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 59,
    "resName": "TYR",
    "chain": "A",
    "ca": [
      21.08,
      21.15,
      16.25
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 60,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      19.07,
      21.35,
      13.0
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 61,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      21.18,
      24.26,
      11.69
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 62,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      20.08,
      24.77,
      8.03
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 63,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      21.66,
      26.85,
      5.24
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 64,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      21.91,
      30.56,
      5.88
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 65,
    "resName": "SER",
    "chain": "A",
    "ca": [
      21.42,
      30.25,
      9.62
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 66,
    "resName": "THR",
    "chain": "A",
    "ca": [
      23.21,
      32.76,
      11.89
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 67,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      25.15,
      31.61,
      14.98
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 68,
    "resName": "HIS",
    "chain": "A",
    "ca": [
      26.18,
      34.13,
      17.65
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 69,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      29.8,
      34.15,
      18.83
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 70,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      30.48,
      35.37,
      22.37
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 71,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      34.15,
      35.47,
      23.48
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 72,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      35.16,
      34.17,
      26.9
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 73,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      38.67,
      35.5,
      27.68
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 74,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      40.87,
      33.8,
      30.25
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 75,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      41.84,
      36.55,
      32.69
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 76,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      40.37,
      39.81,
      33.94
    ],
    "sec": "loop",
    "defaultPlddt": 92
  }
];

// ---------------------------------------------------------------------------
// 2. AUTHENTIC 1TEN TENASCIN-C (PDB 1TEN, 1.40 Å, 89 Res)
// ---------------------------------------------------------------------------
export const TENASCIN_1TEN_COORDS: PdbResidue[] = [
  {
    "resSeq": 1,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      32.05,
      36.23,
      11.76
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 2,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      33.93,
      38.41,
      14.15
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 3,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      32.91,
      42.16,
      14.06
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 4,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      35.65,
      44.84,
      13.35
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 5,
    "resName": "SER",
    "chain": "A",
    "ca": [
      37.43,
      45.78,
      16.61
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 6,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      38.72,
      49.02,
      18.15
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 7,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      36.42,
      51.24,
      16.12
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 8,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      37.29,
      54.85,
      16.72
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 9,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      35.9,
      58.05,
      15.18
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 10,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      38.69,
      60.72,
      15.08
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 11,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      39.52,
      64.03,
      13.37
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 12,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      35.93,
      65.33,
      13.6
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 13,
    "resName": "THR",
    "chain": "A",
    "ca": [
      35.23,
      68.8,
      12.24
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 14,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      31.85,
      70.55,
      11.75
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 15,
    "resName": "THR",
    "chain": "A",
    "ca": [
      31.44,
      68.66,
      8.46
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 16,
    "resName": "THR",
    "chain": "A",
    "ca": [
      33.93,
      65.69,
      8.34
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 17,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      35.01,
      62.62,
      10.39
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 18,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      37.5,
      59.7,
      10.01
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 19,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      36.33,
      56.17,
      11.07
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 20,
    "resName": "THR",
    "chain": "A",
    "ca": [
      39.15,
      53.64,
      11.77
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 21,
    "resName": "TRP",
    "chain": "A",
    "ca": [
      39.04,
      50.03,
      12.96
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 22,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      41.09,
      46.84,
      13.25
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 23,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      40.49,
      44.16,
      10.64
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 24,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      38.32,
      41.19,
      11.86
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 25,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      40.27,
      38.03,
      12.79
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 26,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      38.41,
      35.81,
      10.35
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 27,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      39.01,
      36.19,
      6.61
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 28,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      36.19,
      38.27,
      5.11
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 29,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      35.18,
      39.63,
      1.65
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 30,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      34.56,
      43.07,
      3.06
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 31,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      33.01,
      45.4,
      5.6
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 32,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      29.69,
      47.25,
      5.22
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 33,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      29.76,
      50.67,
      6.92
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 34,
    "resName": "THR",
    "chain": "A",
    "ca": [
      26.43,
      52.5,
      7.47
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 35,
    "resName": "TYR",
    "chain": "A",
    "ca": [
      26.26,
      56.09,
      8.77
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 36,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      23.54,
      58.7,
      9.19
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 37,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      21.99,
      61.25,
      11.62
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 38,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      21.26,
      59.21,
      14.73
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 39,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      17.64,
      60.07,
      15.26
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 40,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      16.57,
      60.28,
      11.61
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 41,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      15.72,
      56.56,
      10.82
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 42,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      15.63,
      57.08,
      7.09
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 43,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      19.06,
      58.77,
      6.89
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 44,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      21.3,
      55.75,
      6.25
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 45,
    "resName": "THR",
    "chain": "A",
    "ca": [
      24.16,
      55.55,
      3.7
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 46,
    "resName": "THR",
    "chain": "A",
    "ca": [
      25.94,
      52.15,
      3.39
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 47,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      29.46,
      51.91,
      1.87
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 48,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      30.83,
      48.45,
      0.97
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 49,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      34.58,
      48.32,
      1.71
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 50,
    "resName": "THR",
    "chain": "A",
    "ca": [
      37.05,
      45.69,
      0.53
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 51,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      38.85,
      43.52,
      3.18
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 52,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      42.06,
      45.52,
      2.85
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 53,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      40.48,
      48.87,
      3.91
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 54,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      40.8,
      49.85,
      7.58
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 55,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      39.61,
      53.52,
      7.59
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 56,
    "resName": "TYR",
    "chain": "A",
    "ca": [
      36.98,
      55.69,
      5.85
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 57,
    "resName": "SER",
    "chain": "A",
    "ca": [
      36.81,
      59.47,
      5.59
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 58,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      33.3,
      61.0,
      5.61
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 59,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      32.5,
      64.55,
      4.38
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 60,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      29.54,
      66.89,
      3.87
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 61,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      28.04,
      66.2,
      7.29
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 62,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      25.75,
      68.65,
      9.08
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 63,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      27.33,
      70.81,
      11.87
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 64,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      26.41,
      70.25,
      15.54
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 65,
    "resName": "THR",
    "chain": "A",
    "ca": [
      24.67,
      67.01,
      14.75
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 66,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      24.82,
      63.6,
      16.41
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 67,
    "resName": "TYR",
    "chain": "A",
    "ca": [
      25.59,
      60.72,
      13.99
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 68,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      25.65,
      56.96,
      14.29
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 69,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      28.03,
      54.59,
      12.4
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 70,
    "resName": "SER",
    "chain": "A",
    "ca": [
      27.5,
      50.81,
      12.21
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 71,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      29.98,
      48.23,
      10.82
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 72,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      29.42,
      44.56,
      9.81
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 73,
    "resName": "SER",
    "chain": "A",
    "ca": [
      32.03,
      42.02,
      8.54
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 74,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      30.86,
      39.99,
      5.54
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 75,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      31.81,
      36.7,
      3.98
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 76,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      29.39,
      35.48,
      1.39
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 77,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      26.13,
      34.6,
      2.9
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 78,
    "resName": "MET",
    "chain": "A",
    "ca": [
      27.41,
      35.4,
      6.4
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 79,
    "resName": "SER",
    "chain": "A",
    "ca": [
      27.73,
      38.64,
      8.34
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 80,
    "resName": "SER",
    "chain": "A",
    "ca": [
      28.97,
      39.47,
      11.82
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 81,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      26.79,
      41.11,
      14.43
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 82,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      26.85,
      44.94,
      13.91
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 83,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      29.07,
      47.13,
      16.11
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 84,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      27.81,
      50.76,
      16.52
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 85,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      29.28,
      54.03,
      17.73
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 86,
    "resName": "THR",
    "chain": "A",
    "ca": [
      27.96,
      57.59,
      17.95
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 87,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      29.9,
      60.88,
      17.38
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 88,
    "resName": "THR",
    "chain": "A",
    "ca": [
      28.89,
      64.59,
      17.13
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 89,
    "resName": "THR",
    "chain": "A",
    "ca": [
      30.11,
      67.19,
      14.6
    ],
    "sec": "loop",
    "defaultPlddt": 92
  }
];

// ---------------------------------------------------------------------------
// 3. AUTHENTIC 2CRO PHAGE 434 CRO (PDB 2CRO, 2.35 Å, 65 Res)
// ---------------------------------------------------------------------------
export const CRO_2CRO_COORDS: PdbResidue[] = [
  {
    "resSeq": 1,
    "resName": "MET",
    "chain": "A",
    "ca": [
      21.35,
      5.23,
      12.33
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 2,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      22.16,
      4.18,
      8.75
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 3,
    "resName": "THR",
    "chain": "A",
    "ca": [
      21.91,
      0.46,
      9.54
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 4,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      18.67,
      -1.45,
      10.17
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 5,
    "resName": "SER",
    "chain": "A",
    "ca": [
      19.84,
      -2.65,
      13.59
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 6,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      20.62,
      0.98,
      14.43
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 7,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      17.35,
      2.23,
      13.07
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 8,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      15.28,
      -0.32,
      15.01
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 9,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      17.15,
      0.2,
      18.28
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 10,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      16.89,
      3.98,
      18.06
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 11,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      13.13,
      3.91,
      17.21
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 12,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      12.43,
      1.24,
      19.87
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 13,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      14.12,
      3.48,
      22.43
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 14,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      12.38,
      6.63,
      21.14
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 15,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      9.08,
      4.87,
      21.86
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 16,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      10.32,
      4.04,
      25.36
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 17,
    "resName": "MET",
    "chain": "A",
    "ca": [
      10.12,
      0.27,
      24.82
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 18,
    "resName": "THR",
    "chain": "A",
    "ca": [
      12.2,
      -2.68,
      25.95
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 19,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      13.12,
      -5.53,
      23.56
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 20,
    "resName": "THR",
    "chain": "A",
    "ca": [
      10.6,
      -7.66,
      25.45
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 21,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      7.75,
      -5.25,
      24.99
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 22,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      8.69,
      -4.83,
      21.31
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 23,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      8.63,
      -8.63,
      21.01
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 24,
    "resName": "THR",
    "chain": "A",
    "ca": [
      5.24,
      -9.02,
      22.75
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 25,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      3.52,
      -6.29,
      20.68
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 26,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      4.95,
      -7.61,
      17.39
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 27,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      4.32,
      -11.22,
      18.35
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 28,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      7.87,
      -12.5,
      17.68
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 29,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      10.62,
      -14.02,
      19.81
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 30,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      12.64,
      -11.65,
      21.97
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 31,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      15.76,
      -13.47,
      20.68
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 32,
    "resName": "SER",
    "chain": "A",
    "ca": [
      14.65,
      -12.26,
      17.24
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 33,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      14.99,
      -8.61,
      18.24
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 34,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      18.42,
      -8.98,
      19.88
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 35,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      19.76,
      -10.61,
      16.69
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 36,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      18.36,
      -7.77,
      14.6
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 37,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      19.64,
      -5.12,
      17.01
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 38,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      23.0,
      -6.91,
      17.33
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 39,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      23.21,
      -6.69,
      13.51
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 40,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      23.16,
      -10.48,
      12.87
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 41,
    "resName": "THR",
    "chain": "A",
    "ca": [
      19.83,
      -10.63,
      11.04
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 42,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      20.01,
      -8.28,
      8.07
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 43,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      16.73,
      -9.42,
      6.52
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 44,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      14.13,
      -9.92,
      9.26
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 45,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      11.29,
      -12.37,
      8.63
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 46,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      8.59,
      -10.33,
      10.45
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 47,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      9.73,
      -6.8,
      9.5
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 48,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      6.15,
      -5.75,
      8.8
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 49,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      4.84,
      -6.71,
      12.26
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 50,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      7.94,
      -5.21,
      13.88
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 51,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      7.31,
      -1.93,
      12.02
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 52,
    "resName": "MET",
    "chain": "A",
    "ca": [
      3.63,
      -1.98,
      12.97
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 53,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      4.62,
      -2.18,
      16.67
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 54,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      7.09,
      0.74,
      16.17
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 55,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      4.4,
      2.83,
      14.44
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 56,
    "resName": "CYS",
    "chain": "A",
    "ca": [
      6.6,
      3.46,
      11.37
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 57,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      6.89,
      2.59,
      7.68
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 58,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      8.36,
      -0.85,
      7.05
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 59,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      10.14,
      0.46,
      3.93
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 60,
    "resName": "TRP",
    "chain": "A",
    "ca": [
      11.68,
      3.22,
      6.05
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 61,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      12.81,
      0.66,
      8.63
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 62,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      14.41,
      -1.67,
      6.08
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 63,
    "resName": "TYR",
    "chain": "A",
    "ca": [
      16.04,
      0.89,
      3.77
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 64,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      16.03,
      4.12,
      5.8
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 65,
    "resName": "THR",
    "chain": "A",
    "ca": [
      13.92,
      6.25,
      3.43
    ],
    "sec": "loop",
    "defaultPlddt": 92
  }
];

// ---------------------------------------------------------------------------
// 4. AUTHENTIC 3CLN CALMODULIN (PDB 3CLN, 2.20 Å, 71 Res)
// ---------------------------------------------------------------------------
export const CALMODULIN_3CLN_COORDS: PdbResidue[] = [
  {
    "resSeq": 1,
    "resName": "THR",
    "chain": "A",
    "ca": [
      -22.13,
      30.52,
      31.54
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 2,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      -23.24,
      32.55,
      34.59
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 3,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      -19.9,
      31.89,
      36.32
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 4,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      -18.22,
      32.42,
      32.94
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 5,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      -19.5,
      35.97,
      32.39
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 6,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      -18.47,
      36.76,
      35.98
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 7,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      -14.9,
      35.67,
      35.19
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 8,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      -15.01,
      37.78,
      32.01
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 9,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      -16.47,
      40.66,
      34.03
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 10,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      -13.48,
      40.48,
      36.37
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 11,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      -11.09,
      40.67,
      33.42
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 12,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      -13.03,
      43.68,
      31.97
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 13,
    "resName": "SER",
    "chain": "A",
    "ca": [
      -12.79,
      45.6,
      35.23
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 14,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      -8.97,
      45.63,
      35.19
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 15,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      -9.15,
      47.63,
      31.97
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 16,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      -12.16,
      49.79,
      32.95
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 17,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      -10.31,
      51.94,
      35.52
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 18,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      -13.1,
      54.47,
      36.11
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 19,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      -15.84,
      51.85,
      35.88
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 20,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      -18.03,
      53.72,
      33.37
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 21,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      -18.61,
      50.53,
      31.35
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 22,
    "resName": "THR",
    "chain": "A",
    "ca": [
      -16.14,
      51.15,
      28.52
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 23,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      -12.49,
      50.84,
      27.67
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 24,
    "resName": "THR",
    "chain": "A",
    "ca": [
      -10.72,
      53.81,
      26.19
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 25,
    "resName": "THR",
    "chain": "A",
    "ca": [
      -7.36,
      54.12,
      24.5
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 26,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      -6.15,
      55.8,
      27.72
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 27,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      -7.32,
      52.99,
      30.03
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 28,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      -5.89,
      50.38,
      27.65
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 29,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      -2.76,
      52.51,
      27.73
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 30,
    "resName": "THR",
    "chain": "A",
    "ca": [
      -2.35,
      52.39,
      31.56
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 31,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      -2.69,
      48.6,
      31.67
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 32,
    "resName": "MET",
    "chain": "A",
    "ca": [
      -0.18,
      48.11,
      28.84
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 33,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      2.15,
      50.35,
      30.84
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 34,
    "resName": "SER",
    "chain": "A",
    "ca": [
      1.57,
      48.62,
      34.16
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 35,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      2.79,
      45.65,
      32.15
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 36,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      6.06,
      47.3,
      31.02
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 37,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      4.99,
      48.23,
      27.45
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 38,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      4.59,
      51.89,
      26.44
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 39,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      2.58,
      51.83,
      23.24
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 40,
    "resName": "THR",
    "chain": "A",
    "ca": [
      2.01,
      55.05,
      21.29
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 41,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      -1.51,
      56.48,
      20.91
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 42,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      -1.53,
      55.21,
      17.31
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 43,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      -0.83,
      51.65,
      18.41
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 44,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      -3.46,
      52.01,
      21.16
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 45,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      -5.94,
      53.26,
      18.54
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 46,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      -5.34,
      50.17,
      16.35
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 47,
    "resName": "MET",
    "chain": "A",
    "ca": [
      -5.85,
      47.87,
      19.39
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 48,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      -9.29,
      49.48,
      20.06
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 49,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      -10.45,
      49.53,
      16.4
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 50,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      -9.94,
      45.81,
      16.07
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 51,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      -12.46,
      45.13,
      18.91
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 52,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      -14.73,
      48.15,
      18.59
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 53,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      -17.66,
      46.59,
      16.66
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 54,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      -20.0,
      49.63,
      16.46
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 55,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      -17.34,
      52.34,
      15.93
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 56,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      -18.18,
      54.57,
      18.86
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 57,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      -14.44,
      54.52,
      19.62
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 58,
    "resName": "THR",
    "chain": "A",
    "ca": [
      -14.58,
      52.52,
      22.84
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 59,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      -15.07,
      48.96,
      23.94
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 60,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      -17.97,
      47.85,
      26.07
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 61,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      -18.56,
      44.47,
      27.77
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 62,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      -20.36,
      42.67,
      24.95
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 63,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      -17.57,
      43.7,
      22.49
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 64,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      -14.78,
      42.6,
      24.91
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 65,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      -16.62,
      39.39,
      25.79
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 66,
    "resName": "THR",
    "chain": "A",
    "ca": [
      -17.02,
      38.49,
      22.11
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 67,
    "resName": "MET",
    "chain": "A",
    "ca": [
      -13.37,
      39.37,
      21.29
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 68,
    "resName": "MET",
    "chain": "A",
    "ca": [
      -12.29,
      37.28,
      24.29
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 69,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      -14.45,
      34.24,
      23.43
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 70,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      -13.07,
      33.72,
      19.89
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 71,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      -9.46,
      34.35,
      20.96
    ],
    "sec": "helix",
    "defaultPlddt": 92
  }
];

// ---------------------------------------------------------------------------
// 5. AUTHENTIC 1N5U DESIGNED COILED COIL (PDB 1N5U, 1.95 Å, 91 Res)
// ---------------------------------------------------------------------------
export const COILEDCOIL_1N5U_COORDS: PdbResidue[] = [
  {
    "resSeq": 1,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      57.48,
      8.59,
      6.87
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 2,
    "resName": "HIS",
    "chain": "A",
    "ca": [
      59.52,
      10.42,
      9.53
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 3,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      62.73,
      9.16,
      11.12
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 4,
    "resName": "SER",
    "chain": "A",
    "ca": [
      61.12,
      8.88,
      14.55
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 5,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      57.39,
      8.27,
      14.46
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 6,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      57.06,
      8.65,
      18.23
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 7,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      58.83,
      12.01,
      18.01
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 8,
    "resName": "HIS",
    "chain": "A",
    "ca": [
      56.51,
      13.03,
      15.19
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 9,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      53.44,
      11.99,
      17.18
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 10,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      54.66,
      13.83,
      20.28
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 11,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      55.37,
      17.01,
      18.33
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 12,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      51.96,
      16.99,
      16.7
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 13,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      49.81,
      15.88,
      19.62
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 14,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      51.58,
      17.89,
      22.28
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 15,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      52.85,
      16.37,
      25.52
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 16,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      49.57,
      16.47,
      27.46
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 17,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      47.51,
      14.79,
      24.75
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 18,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      50.31,
      12.3,
      24.04
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 19,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      50.33,
      11.26,
      27.71
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 20,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      46.56,
      10.88,
      27.9
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 21,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      46.47,
      8.81,
      24.71
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 22,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      49.28,
      6.55,
      25.89
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 23,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      47.39,
      6.06,
      29.14
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 24,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      44.23,
      5.06,
      27.27
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 25,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      46.19,
      2.81,
      24.9
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 26,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      47.81,
      0.94,
      27.76
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 27,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      44.63,
      0.76,
      29.81
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 28,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      42.83,
      -0.77,
      26.84
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 29,
    "resName": "TYR",
    "chain": "A",
    "ca": [
      45.35,
      -3.63,
      26.76
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 30,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      46.51,
      -3.96,
      30.39
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 31,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      42.87,
      -3.81,
      31.5
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 32,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      43.82,
      -5.49,
      34.78
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 33,
    "resName": "CYS",
    "chain": "A",
    "ca": [
      46.81,
      -3.43,
      35.89
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 34,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      46.45,
      -0.76,
      38.62
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 35,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      46.24,
      2.95,
      37.83
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 36,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      49.66,
      3.62,
      39.38
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 37,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      51.23,
      0.98,
      37.12
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 38,
    "resName": "HIS",
    "chain": "A",
    "ca": [
      49.8,
      2.73,
      34.09
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 39,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      51.01,
      6.13,
      35.29
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 40,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      54.52,
      4.71,
      35.6
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 41,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      54.28,
      3.18,
      32.14
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 42,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      53.07,
      6.46,
      30.65
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 43,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      55.89,
      8.47,
      32.24
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 44,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      58.45,
      5.97,
      31.06
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 45,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      57.09,
      6.05,
      27.52
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 46,
    "resName": "THR",
    "chain": "A",
    "ca": [
      56.83,
      9.85,
      27.61
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 47,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      60.39,
      10.28,
      28.84
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 48,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      61.54,
      8.09,
      25.98
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 49,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      59.45,
      10.07,
      23.5
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 50,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      61.17,
      13.21,
      24.75
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 51,
    "resName": "THR",
    "chain": "A",
    "ca": [
      64.62,
      11.8,
      23.94
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 52,
    "resName": "CYS",
    "chain": "A",
    "ca": [
      63.34,
      11.19,
      20.42
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 53,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      61.96,
      14.7,
      20.24
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 54,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      65.34,
      16.02,
      21.37
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 55,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      67.0,
      13.77,
      18.77
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 56,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      65.34,
      11.5,
      16.19
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 57,
    "resName": "SER",
    "chain": "A",
    "ca": [
      68.59,
      9.56,
      15.97
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 58,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      68.55,
      8.64,
      19.66
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 59,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      68.52,
      4.89,
      20.34
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 60,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      65.29,
      3.05,
      19.48
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 61,
    "resName": "CYS",
    "chain": "A",
    "ca": [
      63.71,
      6.27,
      18.28
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 62,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      63.51,
      4.96,
      14.73
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 63,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      61.38,
      1.96,
      15.69
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 64,
    "resName": "SER",
    "chain": "A",
    "ca": [
      57.7,
      1.99,
      14.69
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 65,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      54.96,
      2.89,
      17.16
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 66,
    "resName": "HIS",
    "chain": "A",
    "ca": [
      53.63,
      -0.68,
      17.13
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 67,
    "resName": "THR",
    "chain": "A",
    "ca": [
      57.1,
      -2.05,
      17.75
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 68,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      57.72,
      0.31,
      20.67
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 69,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      54.25,
      -0.21,
      22.16
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 70,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      54.43,
      -4.0,
      21.87
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 71,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      57.93,
      -4.09,
      23.34
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 72,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      56.78,
      -2.03,
      26.32
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 73,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      53.81,
      -4.33,
      26.83
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 74,
    "resName": "CYS",
    "chain": "A",
    "ca": [
      56.15,
      -7.3,
      26.83
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 75,
    "resName": "THR",
    "chain": "A",
    "ca": [
      58.33,
      -5.81,
      29.56
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 76,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      55.41,
      -5.92,
      31.99
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 77,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      56.54,
      -8.36,
      34.69
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 78,
    "resName": "THR",
    "chain": "A",
    "ca": [
      53.17,
      -9.95,
      35.48
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 79,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      51.94,
      -10.22,
      31.88
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 80,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      51.58,
      -14.02,
      31.89
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 81,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      50.45,
      -14.29,
      35.52
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 82,
    "resName": "THR",
    "chain": "A",
    "ca": [
      47.72,
      -11.7,
      34.96
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 83,
    "resName": "TYR",
    "chain": "A",
    "ca": [
      46.87,
      -12.01,
      31.27
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 84,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      47.74,
      -15.62,
      30.57
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 85,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      47.99,
      -16.43,
      26.86
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 86,
    "resName": "MET",
    "chain": "A",
    "ca": [
      48.13,
      -12.77,
      25.96
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 87,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      51.71,
      -12.98,
      27.25
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 88,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      52.26,
      -15.5,
      24.45
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 89,
    "resName": "CYS",
    "chain": "A",
    "ca": [
      51.88,
      -12.65,
      21.96
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 90,
    "resName": "CYS",
    "chain": "A",
    "ca": [
      55.37,
      -11.56,
      22.97
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 91,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      56.86,
      -14.59,
      21.23
    ],
    "sec": "helix",
    "defaultPlddt": 92
  }
];

// ---------------------------------------------------------------------------
// 6. AUTHENTIC TFR1 RECEPTOR ECTODOMAIN (PDB 1CX8, 201 Res)
// ---------------------------------------------------------------------------
const TFR1_CHAIN_A: PdbResidue[] = [
  {
    "resSeq": 1,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      7.35,
      24.74,
      -17.99
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 2,
    "resName": "HIS",
    "chain": "A",
    "ca": [
      8.66,
      21.4,
      -16.67
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 3,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      8.93,
      17.75,
      -17.69
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 4,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      8.84,
      15.45,
      -14.68
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 5,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      8.17,
      11.72,
      -14.51
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 6,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      4.82,
      10.94,
      -12.88
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 7,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      3.42,
      7.46,
      -12.26
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 8,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      0.04,
      6.3,
      -13.54
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 9,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      -2.19,
      3.26,
      -13.51
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 10,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      -1.2,
      0.84,
      -16.3
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 11,
    "resName": "SER",
    "chain": "A",
    "ca": [
      -3.82,
      -0.59,
      -18.66
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 12,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      -3.36,
      -3.82,
      -16.69
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 13,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      -5.58,
      -3.9,
      -13.59
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 14,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      -4.1,
      -3.63,
      -10.09
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 15,
    "resName": "SER",
    "chain": "A",
    "ca": [
      -5.62,
      -6.02,
      -7.58
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 16,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      -5.63,
      -7.69,
      -4.18
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 17,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      -6.7,
      -11.33,
      -3.96
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 18,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      -6.83,
      -13.77,
      -1.05
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 19,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      -5.14,
      -17.04,
      -1.91
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 20,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      -3.21,
      -19.94,
      -0.37
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 21,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      0.14,
      -21.51,
      -1.27
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 22,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      -1.65,
      -21.88,
      -4.61
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 23,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      -5.31,
      -22.0,
      -5.73
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 24,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      -6.46,
      -18.37,
      -5.64
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 25,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      -9.55,
      -18.96,
      -3.51
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 26,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      -12.13,
      -16.29,
      -2.58
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 27,
    "resName": "TYR",
    "chain": "A",
    "ca": [
      -13.79,
      -13.71,
      -4.79
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 28,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      -11.67,
      -11.03,
      -6.46
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 29,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      -11.48,
      -9.02,
      -3.22
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 30,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      -10.95,
      -5.88,
      -5.27
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 31,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      -9.42,
      -4.26,
      -8.36
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 32,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      -8.61,
      -0.95,
      -6.58
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 33,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      -10.03,
      2.15,
      -8.28
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 34,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      -7.16,
      4.41,
      -7.23
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 35,
    "resName": "TYR",
    "chain": "A",
    "ca": [
      -3.44,
      3.9,
      -6.69
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 36,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      -0.31,
      4.93,
      -4.82
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 37,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      2.03,
      6.82,
      -7.16
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 38,
    "resName": "TYR",
    "chain": "A",
    "ca": [
      5.72,
      5.98,
      -7.41
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 39,
    "resName": "SER",
    "chain": "A",
    "ca": [
      4.79,
      2.59,
      -5.97
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 40,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      7.13,
      -0.31,
      -6.77
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 41,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      5.86,
      -1.86,
      -9.99
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 42,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      5.58,
      -5.5,
      -9.0
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 43,
    "resName": "THR",
    "chain": "A",
    "ca": [
      3.39,
      -8.28,
      -7.61
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 44,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      3.87,
      -10.47,
      -4.54
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 45,
    "resName": "THR",
    "chain": "A",
    "ca": [
      1.9,
      -12.57,
      -2.08
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 46,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      2.2,
      -13.7,
      1.52
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 47,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      0.96,
      -13.17,
      5.07
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 48,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      -0.97,
      -9.98,
      5.86
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 49,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      -0.27,
      -8.14,
      9.14
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 50,
    "resName": "HIS",
    "chain": "A",
    "ca": [
      -2.22,
      -5.05,
      10.2
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 51,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      0.01,
      -2.35,
      11.71
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 52,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      -2.4,
      0.41,
      12.79
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 53,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      -1.73,
      3.82,
      11.23
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 54,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      1.03,
      3.15,
      8.73
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 55,
    "resName": "THR",
    "chain": "A",
    "ca": [
      3.24,
      1.64,
      11.41
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 56,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      3.93,
      5.24,
      12.41
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 57,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      7.46,
      3.82,
      12.64
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 58,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      6.44,
      3.69,
      16.3
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 59,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      3.57,
      1.22,
      15.99
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 60,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      5.97,
      -1.27,
      14.37
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 61,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      6.95,
      -2.12,
      17.95
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 62,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      4.03,
      -4.57,
      18.17
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 63,
    "resName": "TYR",
    "chain": "A",
    "ca": [
      3.82,
      -8.34,
      18.8
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 64,
    "resName": "THR",
    "chain": "A",
    "ca": [
      3.35,
      -9.95,
      15.36
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 65,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      6.47,
      -9.57,
      13.14
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 66,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      6.25,
      -8.26,
      9.56
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 67,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      9.54,
      -9.93,
      8.68
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 68,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      8.6,
      -10.91,
      5.11
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 69,
    "resName": "SER",
    "chain": "A",
    "ca": [
      4.85,
      -10.34,
      4.79
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 70,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      2.35,
      -7.89,
      3.3
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 71,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      1.0,
      -5.22,
      5.64
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 72,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      -2.21,
      -3.24,
      6.12
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 73,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      -2.33,
      0.28,
      7.58
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 74,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      -4.82,
      3.06,
      8.17
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 75,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      -4.54,
      6.4,
      6.4
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 76,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      -3.64,
      8.78,
      9.19
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 77,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      -0.98,
      10.12,
      11.55
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 78,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      1.76,
      9.93,
      8.91
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 79,
    "resName": "THR",
    "chain": "A",
    "ca": [
      2.2,
      9.99,
      5.13
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 80,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      1.94,
      6.95,
      2.86
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 81,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      5.57,
      7.6,
      1.96
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 82,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      6.52,
      7.15,
      5.61
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 83,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      4.05,
      4.32,
      6.2
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 84,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      5.61,
      2.35,
      3.35
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 85,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      9.17,
      3.38,
      4.22
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 86,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      8.88,
      1.92,
      7.73
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 87,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      7.11,
      -1.19,
      6.46
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 88,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      10.08,
      -1.87,
      4.2
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 89,
    "resName": "SER",
    "chain": "A",
    "ca": [
      12.62,
      -0.9,
      6.84
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 90,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      11.23,
      -3.9,
      8.73
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 91,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      11.66,
      -6.09,
      5.64
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 92,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      7.98,
      -6.28,
      4.74
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 93,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      6.63,
      -6.38,
      1.17
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 94,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      3.49,
      -4.8,
      -0.19
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 95,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      1.41,
      -2.36,
      1.83
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 96,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      -2.3,
      -1.66,
      1.67
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 97,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      -3.78,
      1.63,
      2.85
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 98,
    "resName": "TYR",
    "chain": "A",
    "ca": [
      -7.48,
      1.94,
      3.74
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 99,
    "resName": "MET",
    "chain": "A",
    "ca": [
      -9.75,
      4.56,
      5.3
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 100,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      -11.36,
      2.97,
      8.38
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 101,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      -14.83,
      4.05,
      9.55
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 102,
    "resName": "THR",
    "chain": "A",
    "ca": [
      -13.91,
      5.76,
      12.85
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 103,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      -11.17,
      7.94,
      11.32
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 104,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      -13.03,
      8.32,
      8.04
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 105,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      -16.83,
      8.6,
      8.65
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 106,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      -17.69,
      8.2,
      4.97
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 107,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      -21.11,
      6.64,
      4.36
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 108,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      -19.86,
      4.94,
      1.18
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 109,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      -17.42,
      2.09,
      1.84
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 110,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      -16.97,
      1.34,
      -1.86
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 111,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      -14.87,
      4.5,
      -2.15
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 112,
    "resName": "SER",
    "chain": "A",
    "ca": [
      -11.24,
      4.51,
      -3.31
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 113,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      -8.53,
      7.17,
      -2.88
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 114,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      -5.27,
      8.37,
      -4.49
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 115,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      -1.79,
      7.97,
      -3.05
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 116,
    "resName": "HIS",
    "chain": "A",
    "ca": [
      1.75,
      9.34,
      -3.16
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 117,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      4.52,
      7.1,
      -1.74
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 118,
    "resName": "HIS",
    "chain": "A",
    "ca": [
      7.61,
      9.26,
      -2.42
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 119,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      9.7,
      9.87,
      0.68
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 120,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      10.6,
      13.29,
      -0.64
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 121,
    "resName": "THR",
    "chain": "A",
    "ca": [
      9.38,
      16.3,
      -2.58
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 122,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      9.0,
      16.68,
      -6.33
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 123,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      10.2,
      14.5,
      -9.22
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 124,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      12.1,
      11.6,
      -7.58
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 125,
    "resName": "TYR",
    "chain": "A",
    "ca": [
      14.88,
      11.66,
      -10.17
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 126,
    "resName": "THR",
    "chain": "A",
    "ca": [
      15.94,
      15.34,
      -10.06
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 127,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      17.01,
      15.77,
      -6.34
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 128,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      18.37,
      19.29,
      -5.85
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 129,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      18.77,
      19.96,
      -9.56
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 130,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      15.98,
      20.55,
      -12.15
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 131,
    "resName": "SER",
    "chain": "A",
    "ca": [
      14.77,
      17.93,
      -14.64
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 132,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      15.01,
      17.81,
      -18.43
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 133,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      13.53,
      15.54,
      -21.12
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 134,
    "resName": "HIS",
    "chain": "A",
    "ca": [
      13.12,
      11.79,
      -20.76
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 135,
    "resName": "THR",
    "chain": "A",
    "ca": [
      15.23,
      11.45,
      -23.89
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 136,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      17.93,
      13.08,
      -21.79
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 137,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      18.75,
      11.99,
      -18.21
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 138,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      16.2,
      9.14,
      -17.92
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 139,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      17.08,
      7.08,
      -14.82
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 140,
    "resName": "SER",
    "chain": "A",
    "ca": [
      14.35,
      4.62,
      -13.76
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 141,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      13.81,
      5.08,
      -9.99
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 142,
    "resName": "SER",
    "chain": "A",
    "ca": [
      14.57,
      3.79,
      -6.46
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 143,
    "resName": "SER",
    "chain": "A",
    "ca": [
      16.21,
      7.17,
      -5.88
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 144,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      14.3,
      7.49,
      -2.61
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 145,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      11.34,
      5.48,
      -3.87
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 146,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      9.5,
      2.51,
      -2.21
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 147,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      10.82,
      -0.63,
      -3.93
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 148,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      7.79,
      -2.3,
      -2.35
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 149,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      4.32,
      -2.38,
      -3.95
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 150,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      1.88,
      -0.01,
      -2.28
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 151,
    "resName": "GLN",
    "chain": "A",
    "ca": [
      -1.84,
      -0.13,
      -2.98
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 152,
    "resName": "THR",
    "chain": "A",
    "ca": [
      -4.77,
      1.91,
      -1.7
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 153,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      -7.77,
      -0.26,
      -0.76
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 154,
    "resName": "SER",
    "chain": "A",
    "ca": [
      -11.47,
      0.54,
      -0.27
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 155,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      -12.96,
      0.1,
      3.23
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 156,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      -15.25,
      -2.54,
      1.76
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 157,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      -12.17,
      -4.45,
      0.57
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 158,
    "resName": "ALA",
    "chain": "A",
    "ca": [
      -10.55,
      -3.96,
      3.97
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 159,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      -13.67,
      -5.49,
      5.53
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 160,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      -13.24,
      -8.64,
      3.46
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 161,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      -9.52,
      -8.92,
      4.23
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 162,
    "resName": "PHE",
    "chain": "A",
    "ca": [
      -10.19,
      -8.82,
      7.97
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 163,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      -12.89,
      -11.38,
      7.24
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 164,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      -10.08,
      -13.8,
      6.41
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 165,
    "resName": "MET",
    "chain": "A",
    "ca": [
      -7.94,
      -13.02,
      9.44
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 166,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      -7.64,
      -14.84,
      12.78
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 167,
    "resName": "GLY",
    "chain": "A",
    "ca": [
      -6.01,
      -12.15,
      14.96
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 168,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      -8.08,
      -9.56,
      16.82
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 169,
    "resName": "CYS",
    "chain": "A",
    "ca": [
      -7.72,
      -5.75,
      16.67
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 170,
    "resName": "PRO",
    "chain": "A",
    "ca": [
      -6.63,
      -4.05,
      19.99
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 171,
    "resName": "SER",
    "chain": "A",
    "ca": [
      -8.33,
      -1.27,
      21.95
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 172,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      -4.96,
      0.5,
      22.17
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 173,
    "resName": "TRP",
    "chain": "A",
    "ca": [
      -5.77,
      1.42,
      18.55
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 174,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      -8.21,
      4.32,
      18.97
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 175,
    "resName": "THR",
    "chain": "A",
    "ca": [
      -10.42,
      2.58,
      16.39
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 176,
    "resName": "ASP",
    "chain": "A",
    "ca": [
      -13.53,
      0.41,
      16.49
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 177,
    "resName": "SER",
    "chain": "A",
    "ca": [
      -14.35,
      -3.3,
      16.0
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 178,
    "resName": "THR",
    "chain": "A",
    "ca": [
      -14.17,
      -5.36,
      12.77
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 179,
    "resName": "CYS",
    "chain": "A",
    "ca": [
      -10.42,
      -5.54,
      12.08
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 180,
    "resName": "ARG",
    "chain": "A",
    "ca": [
      -8.06,
      -8.38,
      12.86
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 181,
    "resName": "MET",
    "chain": "A",
    "ca": [
      -4.28,
      -8.4,
      13.22
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 182,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      -3.2,
      -11.3,
      11.02
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 183,
    "resName": "THR",
    "chain": "A",
    "ca": [
      -4.86,
      -13.28,
      8.24
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 184,
    "resName": "SER",
    "chain": "A",
    "ca": [
      -6.09,
      -16.75,
      9.15
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 185,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      -3.08,
      -19.06,
      8.73
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 186,
    "resName": "SER",
    "chain": "A",
    "ca": [
      -5.21,
      -21.3,
      6.49
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 187,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      -4.42,
      -18.85,
      3.69
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 188,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      -2.69,
      -15.62,
      2.61
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 189,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      -3.11,
      -12.65,
      0.22
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 190,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      -1.48,
      -11.55,
      -3.04
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 191,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      -0.88,
      -7.93,
      -4.07
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 192,
    "resName": "THR",
    "chain": "A",
    "ca": [
      -0.41,
      -7.07,
      -7.74
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 193,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      0.32,
      -3.49,
      -8.81
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 194,
    "resName": "SER",
    "chain": "A",
    "ca": [
      1.11,
      -2.63,
      -12.41
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 195,
    "resName": "ASN",
    "chain": "A",
    "ca": [
      1.74,
      1.09,
      -12.73
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 196,
    "resName": "VAL",
    "chain": "A",
    "ca": [
      3.79,
      2.91,
      -15.31
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 197,
    "resName": "LEU",
    "chain": "A",
    "ca": [
      5.8,
      6.12,
      -15.44
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 198,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      4.51,
      8.86,
      -17.73
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 199,
    "resName": "GLU",
    "chain": "A",
    "ca": [
      6.48,
      11.99,
      -18.61
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 200,
    "resName": "ILE",
    "chain": "A",
    "ca": [
      4.1,
      14.92,
      -18.37
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 201,
    "resName": "LYS",
    "chain": "A",
    "ca": [
      4.47,
      18.63,
      -18.85
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  }
];

// ---------------------------------------------------------------------------
// 7. AUTHENTIC CAMELID VHH NANOBODY (PDB 1I3V, 125 Res)
// ---------------------------------------------------------------------------
const VHH_CHAIN_B: PdbResidue[] = [
  {
    "resSeq": 1,
    "resName": "GLN",
    "chain": "B",
    "ca": [
      24.19,
      31.51,
      -6.44
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 2,
    "resName": "VAL",
    "chain": "B",
    "ca": [
      24.12,
      31.94,
      -2.61
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 3,
    "resName": "GLN",
    "chain": "B",
    "ca": [
      26.06,
      33.88,
      -0.03
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 4,
    "resName": "LEU",
    "chain": "B",
    "ca": [
      26.25,
      32.35,
      3.42
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 5,
    "resName": "GLN",
    "chain": "B",
    "ca": [
      27.08,
      34.09,
      6.66
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 6,
    "resName": "GLU",
    "chain": "B",
    "ca": [
      27.3,
      32.33,
      10.0
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 7,
    "resName": "SER",
    "chain": "B",
    "ca": [
      26.66,
      34.11,
      13.27
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 8,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      26.1,
      33.42,
      16.94
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 9,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      29.65,
      32.5,
      17.82
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 10,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      31.17,
      33.72,
      21.05
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 11,
    "resName": "LEU",
    "chain": "B",
    "ca": [
      32.89,
      32.81,
      24.26
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 12,
    "resName": "VAL",
    "chain": "B",
    "ca": [
      30.91,
      30.36,
      26.32
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 13,
    "resName": "GLN",
    "chain": "B",
    "ca": [
      31.53,
      28.23,
      29.37
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 14,
    "resName": "ALA",
    "chain": "B",
    "ca": [
      31.75,
      24.47,
      29.28
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 15,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      28.34,
      22.93,
      29.79
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 16,
    "resName": "ASP",
    "chain": "B",
    "ca": [
      26.48,
      25.84,
      28.16
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 17,
    "resName": "SER",
    "chain": "B",
    "ca": [
      24.5,
      25.8,
      24.93
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 18,
    "resName": "LEU",
    "chain": "B",
    "ca": [
      24.92,
      28.07,
      21.93
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 19,
    "resName": "LYS",
    "chain": "B",
    "ca": [
      22.76,
      28.48,
      18.83
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 20,
    "resName": "LEU",
    "chain": "B",
    "ca": [
      24.45,
      29.26,
      15.54
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 21,
    "resName": "SER",
    "chain": "B",
    "ca": [
      22.75,
      30.63,
      12.43
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 22,
    "resName": "CYS",
    "chain": "B",
    "ca": [
      23.7,
      30.21,
      8.81
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 23,
    "resName": "GLU",
    "chain": "B",
    "ca": [
      21.8,
      32.92,
      6.9
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 24,
    "resName": "ALA",
    "chain": "B",
    "ca": [
      21.72,
      32.98,
      3.12
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 25,
    "resName": "SER",
    "chain": "B",
    "ca": [
      21.48,
      36.01,
      0.93
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 26,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      21.07,
      36.33,
      -2.81
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 27,
    "resName": "ASP",
    "chain": "B",
    "ca": [
      18.92,
      33.22,
      -3.03
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 28,
    "resName": "SER",
    "chain": "B",
    "ca": [
      16.64,
      31.12,
      -0.93
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 29,
    "resName": "ILE",
    "chain": "B",
    "ca": [
      18.27,
      28.54,
      1.29
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 30,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      15.2,
      26.34,
      0.63
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 31,
    "resName": "THR",
    "chain": "B",
    "ca": [
      16.59,
      24.58,
      -2.46
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 32,
    "resName": "TYR",
    "chain": "B",
    "ca": [
      20.09,
      23.8,
      -1.12
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 33,
    "resName": "VAL",
    "chain": "B",
    "ca": [
      21.25,
      20.98,
      1.13
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 34,
    "resName": "ILE",
    "chain": "B",
    "ca": [
      23.05,
      22.7,
      4.05
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 35,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      25.95,
      21.25,
      5.96
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 36,
    "resName": "TRP",
    "chain": "B",
    "ca": [
      27.85,
      22.26,
      9.09
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 37,
    "resName": "PHE",
    "chain": "B",
    "ca": [
      31.59,
      21.85,
      9.52
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 38,
    "resName": "ARG",
    "chain": "B",
    "ca": [
      34.06,
      23.09,
      12.14
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 39,
    "resName": "GLN",
    "chain": "B",
    "ca": [
      37.85,
      23.36,
      12.22
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 40,
    "resName": "ALA",
    "chain": "B",
    "ca": [
      39.94,
      23.37,
      15.41
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 41,
    "resName": "PRO",
    "chain": "B",
    "ca": [
      43.05,
      25.69,
      15.34
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 42,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      45.47,
      23.11,
      13.85
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 43,
    "resName": "LYS",
    "chain": "B",
    "ca": [
      43.2,
      20.25,
      12.82
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 44,
    "resName": "GLU",
    "chain": "B",
    "ca": [
      41.47,
      19.3,
      9.6
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 45,
    "resName": "ARG",
    "chain": "B",
    "ca": [
      38.0,
      20.65,
      8.82
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 46,
    "resName": "ILE",
    "chain": "B",
    "ca": [
      35.49,
      18.08,
      10.01
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 47,
    "resName": "TYR",
    "chain": "B",
    "ca": [
      31.89,
      17.38,
      9.05
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 48,
    "resName": "LEU",
    "chain": "B",
    "ca": [
      29.22,
      17.88,
      11.75
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 49,
    "resName": "ALA",
    "chain": "B",
    "ca": [
      25.68,
      17.68,
      10.29
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 50,
    "resName": "THR",
    "chain": "B",
    "ca": [
      23.55,
      18.0,
      7.2
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 51,
    "resName": "ILE",
    "chain": "B",
    "ca": [
      19.92,
      18.98,
      6.71
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 52,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      18.01,
      18.1,
      3.55
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 53,
    "resName": "ARG",
    "chain": "B",
    "ca": [
      15.63,
      20.43,
      1.75
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 54,
    "resName": "ASN",
    "chain": "B",
    "ca": [
      12.78,
      17.91,
      1.52
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 55,
    "resName": "LEU",
    "chain": "B",
    "ca": [
      10.17,
      17.35,
      4.23
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 56,
    "resName": "VAL",
    "chain": "B",
    "ca": [
      10.26,
      13.84,
      5.73
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 57,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      7.2,
      14.61,
      7.83
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 58,
    "resName": "PRO",
    "chain": "B",
    "ca": [
      5.08,
      17.76,
      8.39
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 59,
    "resName": "SER",
    "chain": "B",
    "ca": [
      7.69,
      19.46,
      10.55
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 60,
    "resName": "ASP",
    "chain": "B",
    "ca": [
      10.88,
      17.53,
      9.84
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 61,
    "resName": "PHE",
    "chain": "B",
    "ca": [
      13.43,
      17.8,
      7.05
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 62,
    "resName": "TYR",
    "chain": "B",
    "ca": [
      15.92,
      14.97,
      6.29
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 63,
    "resName": "THR",
    "chain": "B",
    "ca": [
      18.74,
      15.15,
      8.84
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 64,
    "resName": "ARG",
    "chain": "B",
    "ca": [
      22.22,
      13.5,
      9.41
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 65,
    "resName": "TYR",
    "chain": "B",
    "ca": [
      24.78,
      13.92,
      12.24
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 66,
    "resName": "ALA",
    "chain": "B",
    "ca": [
      28.39,
      12.88,
      12.77
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 67,
    "resName": "ASP",
    "chain": "B",
    "ca": [
      29.06,
      10.53,
      15.66
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 68,
    "resName": "SER",
    "chain": "B",
    "ca": [
      30.99,
      13.04,
      17.73
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 69,
    "resName": "VAL",
    "chain": "B",
    "ca": [
      27.94,
      15.33,
      18.04
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 70,
    "resName": "LYS",
    "chain": "B",
    "ca": [
      24.84,
      13.18,
      17.46
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 71,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      22.68,
      13.61,
      20.53
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 72,
    "resName": "ARG",
    "chain": "B",
    "ca": [
      24.23,
      16.97,
      21.52
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 73,
    "resName": "PHE",
    "chain": "B",
    "ca": [
      23.7,
      19.06,
      18.37
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 74,
    "resName": "ALA",
    "chain": "B",
    "ca": [
      20.46,
      19.65,
      16.5
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 75,
    "resName": "VAL",
    "chain": "B",
    "ca": [
      20.24,
      21.27,
      13.06
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 76,
    "resName": "SER",
    "chain": "B",
    "ca": [
      16.98,
      22.96,
      11.99
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 77,
    "resName": "ARG",
    "chain": "B",
    "ca": [
      15.55,
      24.74,
      9.0
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 78,
    "resName": "ASP",
    "chain": "B",
    "ca": [
      13.68,
      28.1,
      8.58
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 79,
    "resName": "ASN",
    "chain": "B",
    "ca": [
      13.16,
      28.77,
      5.02
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 80,
    "resName": "ALA",
    "chain": "B",
    "ca": [
      10.97,
      31.77,
      5.99
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 81,
    "resName": "LYS",
    "chain": "B",
    "ca": [
      13.96,
      33.56,
      7.52
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 82,
    "resName": "ASN",
    "chain": "B",
    "ca": [
      16.43,
      32.14,
      4.93
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 83,
    "resName": "THR",
    "chain": "B",
    "ca": [
      18.24,
      30.52,
      7.84
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 84,
    "resName": "VAL",
    "chain": "B",
    "ca": [
      19.41,
      27.09,
      9.03
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 85,
    "resName": "ASN",
    "chain": "B",
    "ca": [
      20.38,
      26.78,
      12.72
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 86,
    "resName": "LEU",
    "chain": "B",
    "ca": [
      22.72,
      24.6,
      14.7
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 87,
    "resName": "GLN",
    "chain": "B",
    "ca": [
      21.74,
      24.18,
      18.35
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 88,
    "resName": "MET",
    "chain": "B",
    "ca": [
      24.84,
      23.07,
      20.32
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 89,
    "resName": "ASN",
    "chain": "B",
    "ca": [
      24.3,
      21.62,
      23.78
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 90,
    "resName": "SER",
    "chain": "B",
    "ca": [
      26.59,
      20.57,
      26.63
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 91,
    "resName": "LEU",
    "chain": "B",
    "ca": [
      29.64,
      22.18,
      25.08
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 92,
    "resName": "LYS",
    "chain": "B",
    "ca": [
      33.15,
      20.95,
      26.0
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 93,
    "resName": "PRO",
    "chain": "B",
    "ca": [
      36.52,
      22.6,
      25.48
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 94,
    "resName": "GLU",
    "chain": "B",
    "ca": [
      37.09,
      20.19,
      22.6
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 95,
    "resName": "ASP",
    "chain": "B",
    "ca": [
      34.26,
      21.97,
      20.76
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 96,
    "resName": "THR",
    "chain": "B",
    "ca": [
      36.31,
      25.14,
      20.43
    ],
    "sec": "helix",
    "defaultPlddt": 92
  },
  {
    "resSeq": 97,
    "resName": "ALA",
    "chain": "B",
    "ca": [
      36.68,
      25.89,
      16.74
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 98,
    "resName": "VAL",
    "chain": "B",
    "ca": [
      35.58,
      28.1,
      13.84
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 99,
    "resName": "TYR",
    "chain": "B",
    "ca": [
      32.17,
      26.75,
      12.63
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 100,
    "resName": "TYR",
    "chain": "B",
    "ca": [
      31.12,
      26.93,
      8.99
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 101,
    "resName": "CYS",
    "chain": "B",
    "ca": [
      27.98,
      26.17,
      7.05
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 102,
    "resName": "ALA",
    "chain": "B",
    "ca": [
      28.15,
      25.21,
      3.36
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 103,
    "resName": "ALA",
    "chain": "B",
    "ca": [
      25.61,
      24.55,
      0.62
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 104,
    "resName": "LYS",
    "chain": "B",
    "ca": [
      25.34,
      22.06,
      -2.15
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 105,
    "resName": "THR",
    "chain": "B",
    "ca": [
      22.71,
      21.06,
      -4.67
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 106,
    "resName": "THR",
    "chain": "B",
    "ca": [
      22.99,
      17.26,
      -4.6
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 107,
    "resName": "THR",
    "chain": "B",
    "ca": [
      22.63,
      14.64,
      -1.91
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 108,
    "resName": "TRP",
    "chain": "B",
    "ca": [
      25.8,
      12.81,
      -2.94
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 109,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      29.43,
      13.14,
      -1.84
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 110,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      28.49,
      12.6,
      1.76
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 111,
    "resName": "ASN",
    "chain": "B",
    "ca": [
      30.34,
      14.08,
      4.74
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 112,
    "resName": "ASP",
    "chain": "B",
    "ca": [
      33.56,
      15.23,
      3.01
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 113,
    "resName": "PRO",
    "chain": "B",
    "ca": [
      34.17,
      18.99,
      2.91
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 114,
    "resName": "ASN",
    "chain": "B",
    "ca": [
      35.37,
      18.37,
      -0.61
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 115,
    "resName": "ASN",
    "chain": "B",
    "ca": [
      32.32,
      18.76,
      -2.82
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 116,
    "resName": "TRP",
    "chain": "B",
    "ca": [
      30.3,
      21.73,
      -1.56
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 117,
    "resName": "ASN",
    "chain": "B",
    "ca": [
      29.36,
      24.59,
      -3.87
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 118,
    "resName": "TYR",
    "chain": "B",
    "ca": [
      29.16,
      27.55,
      -1.51
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 119,
    "resName": "TRP",
    "chain": "B",
    "ca": [
      30.8,
      28.29,
      1.85
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 120,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      30.31,
      30.72,
      4.68
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 121,
    "resName": "GLN",
    "chain": "B",
    "ca": [
      32.88,
      32.94,
      6.38
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 122,
    "resName": "GLY",
    "chain": "B",
    "ca": [
      33.03,
      30.92,
      9.59
    ],
    "sec": "loop",
    "defaultPlddt": 92
  },
  {
    "resSeq": 123,
    "resName": "THR",
    "chain": "B",
    "ca": [
      32.15,
      31.97,
      13.1
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 124,
    "resName": "GLN",
    "chain": "B",
    "ca": [
      34.4,
      31.46,
      16.13
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  },
  {
    "resSeq": 125,
    "resName": "VAL",
    "chain": "B",
    "ca": [
      33.22,
      29.49,
      19.15
    ],
    "sec": "sheet",
    "defaultPlddt": 92
  }
];

// ---------------------------------------------------------------------------
// 8. TFR1 WITH A VHH MACROMOLECULAR COMPLEX GENERATOR
// ---------------------------------------------------------------------------
export const generateTfR1VhhComplex = (): MacromolecularStructureData => {
  const allResidues: PdbResidue[] = [...TFR1_CHAIN_A, ...VHH_CHAIN_B];
  const centered = centerCoordinates(allResidues);

  const interfaceAtoms: SidechainAtom[] = [
  {
    "name": "CB",
    "element": "C",
    "pos": [
      31.04,
      26.72,
      13.65
    ]
  },
  {
    "name": "CG",
    "element": "C",
    "pos": [
      31.31,
      25.81,
      14.83
    ]
  },
  {
    "name": "CD1",
    "element": "C",
    "pos": [
      32.26,
      26.14,
      15.81
    ]
  },
  {
    "name": "CD2",
    "element": "C",
    "pos": [
      30.64,
      24.59,
      14.96
    ]
  },
  {
    "name": "CE1",
    "element": "C",
    "pos": [
      32.54,
      25.25,
      16.86
    ]
  },
  {
    "name": "CE2",
    "element": "C",
    "pos": [
      30.91,
      23.75,
      15.99
    ]
  },
  {
    "name": "CZ",
    "element": "C",
    "pos": [
      31.86,
      24.08,
      16.93
    ]
  },
  {
    "name": "OH",
    "element": "O",
    "pos": [
      32.13,
      23.11,
      17.86
    ]
  },
  {
    "name": "CB",
    "element": "C",
    "pos": [
      32.22,
      26.55,
      7.95
    ]
  },
  {
    "name": "CG",
    "element": "C",
    "pos": [
      33.57,
      27.15,
      8.15
    ]
  },
  {
    "name": "CD1",
    "element": "C",
    "pos": [
      34.5,
      26.58,
      9.06
    ]
  },
  {
    "name": "CD2",
    "element": "C",
    "pos": [
      33.95,
      28.29,
      7.45
    ]
  },
  {
    "name": "CE1",
    "element": "C",
    "pos": [
      35.76,
      27.15,
      9.25
    ]
  },
  {
    "name": "CE2",
    "element": "C",
    "pos": [
      35.21,
      28.86,
      7.62
    ]
  },
  {
    "name": "CZ",
    "element": "C",
    "pos": [
      36.11,
      28.29,
      8.52
    ]
  },
  {
    "name": "OH",
    "element": "O",
    "pos": [
      37.36,
      28.9,
      8.67
    ]
  },
  {
    "name": "CB",
    "element": "C",
    "pos": [
      26.15,
      20.78,
      -1.96
    ]
  },
  {
    "name": "CG",
    "element": "C",
    "pos": [
      25.67,
      19.88,
      -0.9
    ]
  },
  {
    "name": "CD",
    "element": "C",
    "pos": [
      26.44,
      18.57,
      -0.99
    ]
  },
  {
    "name": "CE",
    "element": "C",
    "pos": [
      25.96,
      17.6,
      0.07
    ]
  },
  {
    "name": "NZ",
    "element": "N",
    "pos": [
      26.5,
      16.26,
      -0.11
    ]
  },
  {
    "name": "CB",
    "element": "C",
    "pos": [
      3.11,
      11.01,
      4.43
    ]
  },
  {
    "name": "OG1",
    "element": "O",
    "pos": [
      4.48,
      10.66,
      4.66
    ]
  },
  {
    "name": "CG2",
    "element": "C",
    "pos": [
      2.84,
      12.41,
      4.96
    ]
  },
  {
    "name": "CB",
    "element": "C",
    "pos": [
      6.14,
      8.99,
      1.71
    ]
  },
  {
    "name": "CB",
    "element": "C",
    "pos": [
      5.57,
      2.72,
      1.86
    ]
  },
  {
    "name": "CG1",
    "element": "C",
    "pos": [
      6.14,
      1.58,
      1.03
    ]
  },
  {
    "name": "CG2",
    "element": "C",
    "pos": [
      4.14,
      3.03,
      1.43
    ]
  }
];
  const interfaceBonds: SidechainBond[] = [
  {
    "from": [
      31.04,
      26.72,
      13.65
    ],
    "to": [
      31.31,
      25.81,
      14.83
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      31.31,
      25.81,
      14.83
    ],
    "to": [
      32.26,
      26.14,
      15.81
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      31.31,
      25.81,
      14.83
    ],
    "to": [
      30.64,
      24.59,
      14.96
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      32.26,
      26.14,
      15.81
    ],
    "to": [
      32.54,
      25.25,
      16.86
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      30.64,
      24.59,
      14.96
    ],
    "to": [
      30.91,
      23.75,
      15.99
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      32.54,
      25.25,
      16.86
    ],
    "to": [
      31.86,
      24.08,
      16.93
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      30.91,
      23.75,
      15.99
    ],
    "to": [
      31.86,
      24.08,
      16.93
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      31.86,
      24.08,
      16.93
    ],
    "to": [
      32.13,
      23.11,
      17.86
    ],
    "elementFrom": "C",
    "elementTo": "O"
  },
  {
    "from": [
      32.22,
      26.55,
      7.95
    ],
    "to": [
      33.57,
      27.15,
      8.15
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      33.57,
      27.15,
      8.15
    ],
    "to": [
      34.5,
      26.58,
      9.06
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      33.57,
      27.15,
      8.15
    ],
    "to": [
      33.95,
      28.29,
      7.45
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      34.5,
      26.58,
      9.06
    ],
    "to": [
      35.76,
      27.15,
      9.25
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      33.95,
      28.29,
      7.45
    ],
    "to": [
      35.21,
      28.86,
      7.62
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      35.76,
      27.15,
      9.25
    ],
    "to": [
      36.11,
      28.29,
      8.52
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      35.21,
      28.86,
      7.62
    ],
    "to": [
      36.11,
      28.29,
      8.52
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      36.11,
      28.29,
      8.52
    ],
    "to": [
      37.36,
      28.9,
      8.67
    ],
    "elementFrom": "C",
    "elementTo": "O"
  },
  {
    "from": [
      26.15,
      20.78,
      -1.96
    ],
    "to": [
      25.67,
      19.88,
      -0.9
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      25.67,
      19.88,
      -0.9
    ],
    "to": [
      26.44,
      18.57,
      -0.99
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      26.44,
      18.57,
      -0.99
    ],
    "to": [
      25.96,
      17.6,
      0.07
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      25.96,
      17.6,
      0.07
    ],
    "to": [
      26.5,
      16.26,
      -0.11
    ],
    "elementFrom": "C",
    "elementTo": "N"
  },
  {
    "from": [
      3.11,
      11.01,
      4.43
    ],
    "to": [
      4.48,
      10.66,
      4.66
    ],
    "elementFrom": "C",
    "elementTo": "O"
  },
  {
    "from": [
      3.11,
      11.01,
      4.43
    ],
    "to": [
      2.84,
      12.41,
      4.96
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      5.57,
      2.72,
      1.86
    ],
    "to": [
      6.14,
      1.58,
      1.03
    ],
    "elementFrom": "C",
    "elementTo": "C"
  },
  {
    "from": [
      5.57,
      2.72,
      1.86
    ],
    "to": [
      4.14,
      3.03,
      1.43
    ],
    "elementFrom": "C",
    "elementTo": "C"
  }
];

  const tyrAtom = interfaceAtoms.find(a => a.name === 'OH');
  const aspAtom = interfaceAtoms.find(a => a.name === 'OD1' || a.name === 'OD2');
  const hydrogenBonds: HydrogenBond[] = [];

  if (tyrAtom && aspAtom) {
    hydrogenBonds.push({
      donor: tyrAtom.pos,
      acceptor: aspAtom.pos,
      donorLabel: 'VHH Tyr99:OH',
      acceptorLabel: 'TfR1 Asp265:OD',
    });
  }

  return {
    id: 'tfr1_vhh',
    title: 'TfR1 with a VHH',
    subtitle: 'Transferrin Receptor 1 with VHH Single-Domain Antibody',
    description:
      'The structure is a VHH, a single-domain antibody fragment, bound to the ectodomain of transferrin receptor 1. The receptor sits on the cells that line the brain\'s blood vessels, which is why a binder to it is worth having; the VHH is the chain to redesign, and the receptor is the reason its binding loops must stay where they are.',
    targetId: 'tfr1',
    isComplex: true,
    chainA: {
      name: 'chain A',
      protein: 'Transferrin receptor 1 (TfR1)',
      description: 'Ectodomain target receptor',
      residuesCount: TFR1_CHAIN_A.length,
      color: 0x333742, // Charcoal / Dark Slate
    },
    chainB: {
      name: 'chain B',
      protein: 'VHH Single-Domain Antibody',
      description: 'Co-designed nanobody binder',
      residuesCount: VHH_CHAIN_B.length,
      color: 0x2563eb, // Cobalt Blue
      designRegions: 'CDR1 (26-35), CDR2 (50-65), CDR3 (95-103)',
    },
    residues: centered,
    interfaceBonds,
    interfaceAtoms,
    hydrogenBonds,
  };
};

// ---------------------------------------------------------------------------
// 9. DYNAMIC MULTI-TARGET RESOLVER
// ---------------------------------------------------------------------------
export const getStructureForModel = (
  modelId: string,
  sequence?: string,
  plddtScores?: number[]
): MacromolecularStructureData => {
  const lower = modelId.toLowerCase();

  // 1. Explicit TfR1 with VHH complex
  if (lower.includes('tfr1') || lower.includes('vhh')) {
    return generateTfR1VhhComplex();
  }

  // 2. 1N5U Coiled Coil
  if (lower.includes('1n5u')) {
    const raw = centerCoordinates(COILEDCOIL_1N5U_COORDS);
    const residues = raw.map((r, i) => ({
      ...r,
      defaultPlddt: plddtScores && plddtScores[i] !== undefined ? plddtScores[i] : r.defaultPlddt,
      isMutated: sequence && sequence[i] ? sequence[i] !== 'MKFLILLFNILCLFPVLAADNHGVSLAEIRKQLQERLKELDAKVEELETKVEELEAKVEELERKVEELERKVEELAAKVEELENKVEELEAK'[i] : false,
    }));
    return {
      id: modelId,
      title: `${modelId} (1N5U Coiled Coil)`,
      subtitle: 'Human Nuclear Receptor Coiled-Coil Domain',
      description: 'Continuous dimeric alpha-helical supercoil structure from target 1n5uA03 (CATH 1.20.5.200).',
      targetId: '1n5uA03',
      isComplex: false,
      chainA: {
        name: 'chain A',
        protein: 'Target 1n5uA03 Coiled Coil',
        description: 'Dimeric alpha-helical bundle',
        residuesCount: residues.length,
        color: 0x2563eb,
      },
      residues,
      interfaceBonds: [],
      interfaceAtoms: [],
      hydrogenBonds: [],
    };
  }

  // 3. 1TEN Tenascin-C
  if (lower.includes('1ten')) {
    const raw = centerCoordinates(TENASCIN_1TEN_COORDS);
    const residues = raw.map((r, i) => ({
      ...r,
      defaultPlddt: plddtScores && plddtScores[i] !== undefined ? plddtScores[i] : r.defaultPlddt,
    }));
    return {
      id: modelId,
      title: `${modelId} (1tenA00 Tenascin-C)`,
      subtitle: 'Fibronectin Type III Domain (CATH 2.60.40.10)',
      description: 'Classic beta-sandwich architecture with 7 antiparallel beta strands.',
      targetId: '1tenA00',
      isComplex: false,
      chainA: {
        name: 'chain A',
        protein: 'Tenascin-C FN3 Domain',
        description: 'Beta-sandwich fold',
        residuesCount: residues.length,
        color: 0x2563eb,
      },
      residues,
      interfaceBonds: [],
      interfaceAtoms: [],
      hydrogenBonds: [],
    };
  }

  // 4. 2CRO Phage 434 Cro
  if (lower.includes('2cro')) {
    const raw = centerCoordinates(CRO_2CRO_COORDS);
    const residues = raw.map((r, i) => ({
      ...r,
      defaultPlddt: plddtScores && plddtScores[i] !== undefined ? plddtScores[i] : r.defaultPlddt,
    }));
    return {
      id: modelId,
      title: `${modelId} (2croA00 Cro Repressor)`,
      subtitle: 'Bacteriophage 434 Repressor (CATH 1.10.10.10)',
      description: 'Helix-turn-helix DNA-binding architecture.',
      targetId: '2croA00',
      isComplex: false,
      chainA: {
        name: 'chain A',
        protein: 'Phage 434 Cro',
        description: 'Helix-turn-helix fold',
        residuesCount: residues.length,
        color: 0x2563eb,
      },
      residues,
      interfaceBonds: [],
      interfaceAtoms: [],
      hydrogenBonds: [],
    };
  }

  // 5. 3CLN Calmodulin
  if (lower.includes('3cln')) {
    const raw = centerCoordinates(CALMODULIN_3CLN_COORDS);
    const residues = raw.map((r, i) => ({
      ...r,
      defaultPlddt: plddtScores && plddtScores[i] !== undefined ? plddtScores[i] : r.defaultPlddt,
    }));
    return {
      id: modelId,
      title: `${modelId} (3clnA00 Calmodulin)`,
      subtitle: 'EF-Hand Calcium Binding Protein (CATH 1.10.240.10)',
      description: 'Calcium-dependent messenger protein with paired EF-hand helix-loop-helix motifs.',
      targetId: '3clnA00',
      isComplex: false,
      chainA: {
        name: 'chain A',
        protein: 'Calmodulin Domain',
        description: 'EF-hand domain',
        residuesCount: residues.length,
        color: 0x2563eb,
      },
      residues,
      interfaceBonds: [],
      interfaceAtoms: [],
      hydrogenBonds: [],
    };
  }

  // 6. Default / 1UBQ Ubiquitin
  const rawUbq = centerCoordinates(UBIQUITIN_1UBQ_COORDS);
  const residues: PdbResidue[] = rawUbq.map((r, i) => {
    const plddt = plddtScores && plddtScores[i] !== undefined ? plddtScores[i] : r.defaultPlddt;
    const isMut = sequence && sequence[i] !== undefined ? sequence[i] !== 'MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG'[i] : false;
    return {
      ...r,
      defaultPlddt: plddt,
      isMutated: isMut,
    };
  });

  // Ubiquitin Hydrophobic patch sticks (Ile44, Val70, Leu8)
  const interfaceAtoms: SidechainAtom[] = [];
  const interfaceBonds: SidechainBond[] = [];

  const res44 = residues[43];
  if (res44) {
    const cb: [number, number, number] = [res44.ca[0] + 1.1, res44.ca[1] + 0.4, res44.ca[2] + 0.2];
    const cg1: [number, number, number] = [cb[0] + 1.1, cb[1] + 0.3, cb[2] - 0.6];
    const cg2: [number, number, number] = [cb[0] + 0.2, cb[1] + 0.1, cb[2] + 1.4];
    const cd1: [number, number, number] = [cg1[0] + 1.1, cg1[1] + 0.4, cg1[2] + 0.2];
    interfaceAtoms.push(
      { name: 'CB', element: 'C', pos: cb },
      { name: 'CG1', element: 'C', pos: cg1 },
      { name: 'CG2', element: 'C', pos: cg2 },
      { name: 'CD1', element: 'C', pos: cd1 }
    );
    interfaceBonds.push(
      { from: res44.ca, to: cb, elementFrom: 'C', elementTo: 'C' },
      { from: cb, to: cg1, elementFrom: 'C', elementTo: 'C' },
      { from: cb, to: cg2, elementFrom: 'C', elementTo: 'C' },
      { from: cg1, to: cd1, elementFrom: 'C', elementTo: 'C' }
    );
  }

  return {
    id: modelId,
    title: `${modelId} (1UBQ Ubiquitin)`,
    subtitle: 'Regulatory Protein (CATH 3.10.20.90, 1.80 Å)',
    description: 'Human ubiquitin regulatory protein. Standard benchmark fold with 5 beta-strands and 1 alpha-helix.',
    targetId: '1UBQ',
    isComplex: false,
    chainA: {
      name: 'chain A',
      protein: 'Ubiquitin Backbone',
      description: 'Alpha/beta beta-grasp fold',
      residuesCount: residues.length,
      color: 0x2563eb,
    },
    residues,
    interfaceBonds,
    interfaceAtoms,
    hydrogenBonds: [],
  };
};
