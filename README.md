import React, { useEffect, useState } from 'react';
import Papa from 'papaparse';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  BarChart, Bar, PieChart, Pie, LineChart, Line,
  XAxis, YAxis, Tooltip, Cell, ResponsiveContainer
} from 'recharts';

const PizzaPulseApp = () => {
  const [data, setData] = useState([]);
  const [kpis, setKpis] = useState({});
  const [revenueOverTime, setRevenueOverTime] = useState([]);
  const [revenueByItem, setRevenueByItem] = useState([]);
  const [revenueByDay, setRevenueByDay] = useState([]);
  const [revenueByHour, setRevenueByHour] = useState([]);

  useEffect(() => {
    fetch('/pizza_sales.csv')
      .then(response => response.text())
      .then(csv => {
        Papa.parse(csv, {
          header: true,
          skipEmptyLines: true,
          complete: results => {
            const parsed = results.data.map(row => ({
              ...row,
              quantity: +row.quantity,
              total_price: +row.total_price,
              order_date: new Date(row.order_date),
              order_time: new Date(`1970-01-01T${row.order_time}`)
            }));
            setData(parsed);
            calculateKPIs(parsed);
            prepareCharts(parsed);
          }
        });
      });
  }, []);

  const calculateKPIs = (data) => {
    const totalRevenue = data.reduce((sum, row) => sum + row.total_price, 0);
    const totalOrders = new Set(data.map(row => row.order_id)).size;
    const totalPizzas = data.reduce((sum, row) => sum + row.quantity, 0);
    const avgOrderValue = totalRevenue / totalOrders;
    const avgPizzasPerOrder = totalPizzas / totalOrders;
    setKpis({
      totalRevenue: `$${totalRevenue.toFixed(2)}`,
      avgOrderValue: `$${avgOrderValue.toFixed(2)}`,
      totalPizzas,
      totalOrders,
      avgPizzasPerOrder: avgPizzasPerOrder.toFixed(2)
    });
  };

  const prepareCharts = (data) => {
    const revenueOverTimeMap = {};
    const revenueByItemMap = {};
    const revenueByDayMap = {};
    const revenueByHourMap = {};

    data.forEach(row => {
      const dateStr = row.order_date.toISOString().split('T')[0];
      revenueOverTimeMap[dateStr] = (revenueOverTimeMap[dateStr] || 0) + row.total_price;

      revenueByItemMap[row.pizza_name] = (revenueByItemMap[row.pizza_name] || 0) + row.total_price;

      const weekday = row.order_date.getDay();
      revenueByDayMap[weekday] = (revenueByDayMap[weekday] || 0) + row.total_price;

      const hour = row.order_time.getHours();
      revenueByHourMap[hour] = (revenueByHourMap[hour] || 0) + row.total_price;
    });

    setRevenueOverTime(Object.entries(revenueOverTimeMap).map(([date, value]) => ({ date, value })));
    setRevenueByItem(Object.entries(revenueByItemMap).map(([name, value]) => ({ name, value }))); 
    setRevenueByDay(Object.entries(revenueByDayMap).map(([day, value]) => ({ day, value })));
    setRevenueByHour(Object.entries(revenueByHourMap).map(([hour, value]) => ({ hour, value })));
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AF19FF'];

  return (
    <div className="p-6 grid gap-6">
      <h1 className="text-3xl font-bold">PizzaPulse – Sales Predictor & Optimizer</h1>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {Object.entries(kpis).map(([key, value]) => (
          <Card key={key}>
            <CardContent>
              <p className="text-sm uppercase font-medium">{key.replace(/([A-Z])/g, ' $1')}</p>
              <p className="text-xl font-semibold">{value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card><CardContent><h2>Revenue Over Time</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={revenueOverTime}><XAxis dataKey="date" /><YAxis /><Tooltip /><Line type="monotone" dataKey="value" stroke="#8884d8" /></LineChart>
          </ResponsiveContainer>
        </CardContent></Card>

        <Card><CardContent><h2>Revenue by Item</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={revenueByItem.slice(0, 5)}><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="value" fill="#82ca9d" /></BarChart>
          </ResponsiveContainer>
        </CardContent></Card>

        <Card><CardContent><h2>Revenue by Day of Week</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={revenueByDay}><XAxis dataKey="day" /><YAxis /><Tooltip /><Bar dataKey="value" fill="#ffc658" /></BarChart>
          </ResponsiveContainer>
        </CardContent></Card>

        <Card><CardContent><h2>Revenue by Hour of Day</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={revenueByHour}><XAxis dataKey="hour" /><YAxis /><Tooltip /><Line type="monotone" dataKey="value" stroke="#ff7300" /></LineChart>
          </ResponsiveContainer>
        </CardContent></Card>
      </div>

      <div className="text-center mt-4">
        <Button className="bg-green-600 hover:bg-green-700 text-white">Generate Predictive Report</Button>
      </div>
    </div>
  );
};

export default PizzaPulseApp;
