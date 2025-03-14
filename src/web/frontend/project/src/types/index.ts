export interface FearGreedData {
  value: number;
  updated_at: string;
}

export interface HistoricalData {
  [key: string]: number;
}

export interface ChartData {
  timestamp: string;
  fearGreedValue: number;
  bitcoinPrice: number;
}