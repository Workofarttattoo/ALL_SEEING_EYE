// Ghost Box | RF dead-space signal simulator for Occult-Cyberpunk
const crypto = require('crypto');

const FRAGMENTS = [
  "unseen", "signal", "aether", "resonance", "void", "binary", "ghost",
  "pattern", "frequency", "echo", "spirit", "machine", "feedback",
  "noise", "dead-space", "station", "flesh", "soul", "socket", "port"
];

function generateNoise(length) {
    return crypto.randomBytes(length).toString('hex');
}

function getSignal() {
    const hop = Math.random() > 0.7;
    const freq = (88 + Math.random() * 20).toFixed(2);
    let fragment = "";

    if (hop) {
        fragment = FRAGMENTS[Math.floor(Math.random() * FRAGMENTS.length)];
    } else {
        fragment = generateNoise(4);
    }

    const category = Math.random() > 0.5 ? 'BIO' : 'AETHER';
    const resonance = Math.random().toFixed(4);

    return {
        frequency: freq + " MHz",
        data: fragment,
        category: category,
        resonance: resonance,
        timestamp: Date.now()
    };
}

module.exports = {
    getSignal,
    deduce: (signal) => {
        // Logic to deduce spirit vs flesh based on signal characteristics
        if (signal.category === 'BIO') {
            return "Deduction: Fleisch-Resonanz (Flesh). Signal is somatic, tied to biological rhythm.";
        } else {
            return "Deduction: Aether-Echo (Spirit). Signal is non-corporeal, origin unknown.";
        }
    }
};
