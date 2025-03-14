import React, { useEffect } from 'react';
import { useStore } from './store';
import GaugeChart from './components/GaugeChart';
import ComparisonChart from './components/ComparisonChart';
import { GaugeCircle, TrendingUp, RefreshCw } from 'lucide-react';

function App() {
  const {
    currentIndex,
    historicalData,
    isLoading,
    error,
    fetchCurrentIndex,
    fetchHistoricalData
  } = useStore();

  useEffect(() => {
    fetchCurrentIndex();
    fetchHistoricalData();

    const interval = setInterval(() => {
      fetchCurrentIndex();
      fetchHistoricalData();
    }, 300000); // Update every 5 minutes

    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          Произошла ошибка при загрузке данных
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <header className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <GaugeCircle className="w-8 h-8 text-blue-600" />
            Индекс Страха и Жадности
          </h1>
        </header>

        {isLoading && !currentIndex ? (
          <div className="flex items-center justify-center p-12">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : (
          <>
            <div className="w-full">
              <div className="bg-white rounded-lg shadow-md p-6 w-full">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <GaugeCircle className="w-6 h-6 text-blue-600" />
                  Текущий индекс
                </h2>
                {currentIndex && (
                  <div className="flex flex-col items-center">
                    <div className="w-full">
                      <GaugeChart value={currentIndex.value} />
                    </div>
                    <p className="text-lg font-medium mt-4">
                        {currentIndex.value <= 39 ? 'Страх' : currentIndex.value <= 59 ? 'Нейтралитет' : 'Жадность'}
                    </p>
                    <p className="text-lg font-regular mt-2">
                      {
                        currentIndex.updated_at 
                          ? new Date(currentIndex.updated_at).toLocaleString('ru-RU', {
                              year: 'numeric',
                              month: '2-digit',
                              day: '2-digit',
                              hour: '2-digit',
                              minute: '2-digit',
                              hour12: false,
                            })
                          : 'Обновлений ещё не было'
                      }
                    </p>
                  </div>
                )}
              </div>
            </div>

            
            {historicalData.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">Индекс в сравнение с биткоином</h2>
                <div className="h-[400px]">
                  <ComparisonChart data={historicalData} />
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default App;