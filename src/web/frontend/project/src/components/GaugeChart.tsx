import React from 'react';
import { PieChart, Pie, Cell } from 'recharts';

interface GaugeChartProps {
  value: number;
}

const GaugeChart: React.FC<GaugeChartProps> = ({ value }) => {
  const data = [
    { value: value },
    { value: 100 - value }
  ];

  const getColor = (value: number) => {
    if (value <= 39) return '#FF4136'; // Fear
    if (value <= 59) return '#FFDC00'; // Neutral
    if (value <= 100) return '#2ECC40'; // Greed
  };

  return (
    <div className="relative w-full max-w-[300px] mx-auto">
      <PieChart width={300} height={150}>
        <Pie
          data={data}
          cx={150}
          cy={150}
          startAngle={180}
          endAngle={0}
          innerRadius={90}
          outerRadius={120}
          paddingAngle={0}
          dataKey="value"
        >
          <Cell fill={getColor(value)} />
          <Cell fill="#f1f1f1" />
        </Pie>
      </PieChart>
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 translate-x-[-15px] translate-y-[15px]">
        <span className="text-4xl font-bold whitespace-nowrap">{value}</span>
      </div>
    </div>
  );
};

export default GaugeChart;