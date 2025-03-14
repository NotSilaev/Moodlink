import { create } from 'zustand';
import { format, subDays } from 'date-fns';
import { ru } from 'date-fns/locale';
import { API_URL } from '../config';
import type { FearGreedData, HistoricalData, ChartData } from '../types';

interface State {
  currentIndex: FearGreedData | null;
  historicalData: ChartData[];
  isLoading: boolean;
  error: string | null;
  fetchCurrentIndex: () => Promise<void>;
  fetchHistoricalData: () => Promise<void>;
}

export const useStore = create<State>((set) => ({
  currentIndex: null,
  historicalData: [],
  isLoading: false,
  error: null,

  fetchCurrentIndex: async () => {
    try {
      set({ isLoading: true });
      const response = await fetch(`${API_URL}/index/latest`);
      const data: FearGreedData = await response.json();
      set({ currentIndex: data, isLoading: false });
    } catch (error) {
      set({ error: 'Ошибка при загрузке текущего индекса', isLoading: false });
    }
  },

  fetchHistoricalData: async () => {
    try {
      set({ isLoading: true });
      const endDate = new Date();
      const startDate = subDays(endDate, 30);
  
      // Форматирование дат в формат yyyy-MM-dd
      const formattedStartDate = format(startDate, 'yyyy-MM-dd');
      const formattedEndDate = format(endDate, 'yyyy-MM-dd');
  
      // Fetch Fear & Greed Index data
      const fngResponse = await fetch(
        `${API_URL}/index/period?start_date=${formattedStartDate}&end_date=${formattedEndDate}`
      );
      const fngData: HistoricalData = await fngResponse.json();
  
      // Fetch Bitcoin price data (using CoinGecko API)
      const btcResponse = await fetch(
        `https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from=${startDate.getTime() / 1000}&to=${endDate.getTime() / 1000}`
      );
      const btcData = await btcResponse.json();
  
      // Combine and format data
      const combinedData: ChartData[] = Object.entries(fngData.index_values).map(
        ([timestamp, value], index) => {
          const date = new Date(timestamp);
          if (isNaN(date.getTime())) {
            console.error('Invalid timestamp:', timestamp);
            return null;
          }
  
          const bitcoinPrice = btcData.prices?.[index]?.[1] || 0;
  
          return {
            timestamp: format(date, 'dd MMM HH:mm', { locale: ru }),
            fearGreedValue: value,
            bitcoinPrice: bitcoinPrice,
          };
        }
      )
      .filter((item) => item !== null)
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  
      set({ historicalData: combinedData, isLoading: false });
    } catch (error) {
      set({ error: 'Ошибка при загрузке исторических данных', isLoading: false });
    }
  },
  
}));