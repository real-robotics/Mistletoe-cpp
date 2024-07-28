// src/utils/voltageUtils.js

export const voltageToPercentage = (voltage) => {
    const voltageMap = [
      { voltage: 25.2, percentage: 100 },
      { voltage: 24.9, percentage: 95 },
      { voltage: 24.67, percentage: 90 },
      { voltage: 24.49, percentage: 85 },
      { voltage: 24.14, percentage: 80 },
      { voltage: 23.9, percentage: 75 },
      { voltage: 23.72, percentage: 70 },
      { voltage: 23.48, percentage: 65 },
      { voltage: 23.25, percentage: 60 },
      { voltage: 23.13, percentage: 55 },
      { voltage: 22.96, percentage: 50 },
      { voltage: 22.77, percentage: 45 },
      { voltage: 22.6, percentage: 40 },
      { voltage: 22.48, percentage: 35 },
      { voltage: 22.36, percentage: 30 },
      { voltage: 22.24, percentage: 25 },
      { voltage: 22.12, percentage: 20 },
      { voltage: 21.65, percentage: 10 },
      { voltage: 19.64, percentage: 0 },
    ];
  
    for (let i = 0; i < voltageMap.length - 1; i++) {
      const v1 = voltageMap[i].voltage;
      const p1 = voltageMap[i].percentage;
      const v2 = voltageMap[i + 1].voltage;
      const p2 = voltageMap[i + 1].percentage;
  
      if (voltage >= v2 && voltage <= v1) {
        const ratio = (voltage - v2) / (v1 - v2);
        return p2 + ratio * (p1 - p2);
      }
    }
  
    if (voltage >= voltageMap[0].voltage) {
      return 100;
    }
    
    if (voltage <= voltageMap[voltageMap.length - 1].voltage) {
      return 0;
    }
  
    return null;
  };
  