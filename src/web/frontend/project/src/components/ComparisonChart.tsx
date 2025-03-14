import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import type { ChartData } from '../types';

interface ComparisonChartProps {
  data: ChartData[];
}

const ComparisonChart: React.FC<ComparisonChartProps> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timestamp" />
        <YAxis yAxisId="left" />
        <YAxis yAxisId="right" orientation="right" />
        <Tooltip />
        <Legend />
        <Line
          yAxisId="left"
          type="monotone"
          dataKey="fearGreedValue"
          stroke="#8884d8"
          name="Индекс страха и жадности"
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="bitcoinPrice"
          stroke="#82ca9d"
          name="Стоимость Bitcoin"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default ComparisonChart;