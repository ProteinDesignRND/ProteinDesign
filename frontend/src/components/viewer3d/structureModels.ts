// 3D Backbone coordinate generator for realistic protein rendering

export interface AtomCoord {
  id: number;
  residueIndex: number;
  residueName: string;
  chain: string;
  x: number;
  y: number;
  z: number;
  secondaryStructure: 'helix' | 'sheet' | 'loop';
  plddt: number;
}

export interface ProteinStructureData {
  targetId: string;
  name: string;
  atoms: AtomCoord[];
  plddtSpectrum: {
    veryHigh: number; // >= 90
    high: number;     // 70-90
    medium: number;   // 50-70
    low: number;      // < 50
  };
}

// Generate realistic structural coordinates based on known fold architectures
export const generateFoldCoordinates = (
  targetId: string,
  sequence: string,
  customPlddt?: number[]
): ProteinStructureData => {
  const atoms: AtomCoord[] = [];
  const n = sequence.length;

  const aa3Map: Record<string, string> = {
    A: 'ALA', R: 'ARG', N: 'ASN', D: 'ASP', C: 'CYS',
    E: 'GLU', Q: 'GLN', G: 'GLY', H: 'HIS', I: 'ILE',
    L: 'LEU', K: 'LYS', M: 'MET', F: 'PHE', P: 'PRO',
    S: 'SER', T: 'THR', W: 'TRP', Y: 'TYR', V: 'VAL'
  };

  // Fold generation templates based on architecture
  const isCoiledCoil = targetId.toLowerCase().includes('1n5u');
  const isUbiquitin = targetId.toLowerCase().includes('1ubq');

  let currentX = 0;
  let currentY = 0;
  let currentZ = 0;

  for (let i = 0; i < n; i++) {
    const aa = sequence[i] || 'A';
    const aa3 = aa3Map[aa] || 'ALA';
    let sec: 'helix' | 'sheet' | 'loop' = 'loop';
    let plddtVal = customPlddt && customPlddt[i] !== undefined
      ? customPlddt[i]
      : 86 + Math.round(Math.sin(i * 0.3) * 10);

    if (isCoiledCoil) {
      // Long continuous alpha-helix bundle
      sec = 'helix';
      const angle = i * 0.65;
      const radius = 8.5;
      currentX = radius * Math.cos(angle);
      currentY = (i - n / 2) * 1.5;
      currentZ = radius * Math.sin(angle);
    } else if (isUbiquitin) {
      // Ubiquitin: Beta-strands (1-7, 10-17, 40-45, 65-71) and Alpha-helix (23-34)
      if (i >= 22 && i <= 34) {
        sec = 'helix';
        const angle = (i - 22) * 0.7;
        currentX = 14 + 6 * Math.cos(angle);
        currentY = (i - 28) * 1.5;
        currentZ = 6 * Math.sin(angle);
      } else if ((i >= 1 && i <= 7) || (i >= 10 && i <= 17) || (i >= 40 && i <= 46) || (i >= 65 && i <= 71)) {
        sec = 'sheet';
        const sheetIdx = i < 20 ? 0 : i < 50 ? 1 : 2;
        currentX = (sheetIdx - 1) * 7.5;
        currentY = ((i % 10) - 5) * 3.2;
        currentZ = -10 + Math.sin(i * 0.8) * 3;
      } else {
        sec = 'loop';
        currentX = Math.cos(i * 0.5) * 16;
        currentY = Math.sin(i * 0.4) * 14;
        currentZ = Math.cos(i * 0.3) * 12;
      }
    } else {
      // Generic globular domain with alternating secondary elements
      const mod = i % 25;
      if (mod < 10) {
        sec = 'helix';
        currentX = 12 * Math.cos(i * 0.6);
        currentY = (i - n / 2) * 1.3;
        currentZ = 12 * Math.sin(i * 0.6);
      } else if (mod >= 13 && mod < 20) {
        sec = 'sheet';
        currentX = (mod - 16) * 3.8;
        currentY = (i - n / 2) * 1.4;
        currentZ = -8 + (i % 4) * 2;
      } else {
        sec = 'loop';
        currentX = Math.sin(i * 0.5) * 15;
        currentY = (i - n / 2) * 1.4;
        currentZ = Math.cos(i * 0.4) * 14;
      }
    }

    atoms.push({
      id: i + 1,
      residueIndex: i + 1,
      residueName: aa3,
      chain: 'A',
      x: currentX,
      y: currentY,
      z: currentZ,
      secondaryStructure: sec,
      plddt: Math.max(35, Math.min(99, plddtVal)),
    });
  }

  // Calculate pLDDT spectrum shares
  let veryHigh = 0;
  let high = 0;
  let medium = 0;
  let low = 0;

  atoms.forEach((a) => {
    if (a.plddt >= 90) veryHigh++;
    else if (a.plddt >= 70) high++;
    else if (a.plddt >= 50) medium++;
    else low++;
  });

  return {
    targetId,
    name: targetId,
    atoms,
    plddtSpectrum: {
      veryHigh: Math.round((veryHigh / n) * 100),
      high: Math.round((high / n) * 100),
      medium: Math.round((medium / n) * 100),
      low: Math.round((low / n) * 100),
    },
  };
};

export const getPlddtColor = (score: number): string => {
  if (score >= 90) return '#0053D6'; // Very high (deep blue)
  if (score >= 70) return '#65CBF3'; // High (cyan)
  if (score >= 50) return '#FFDB13'; // Medium (yellow)
  return '#FF7D45';                  // Low (orange)
};
