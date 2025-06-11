// Step 1: Define the Scope and Objective
// Objective: Analyze sales revenue data to identify trends and understand key influencing factors

// Step 2: Data Collection
// Using the pizza_sales.csv dataset with the following assumed columns:
// TransactionID, Date, Time, Item, Quantity, Price, Revenue

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

  // Step 3: Data Preparation
  // Clean and parse the CSV into usable JS objects
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
              quantity: +row.Quantity,
              total_price: +row.Revenue,
              order_date: new Date(row.Date),
              order_time: new Date(`1970-01-01T${row.Time}`),
              item: row.Item
            }));
            setData(parsed);
            calculateKPIs(parsed);
            generateCharts(parsed);
          }
        });
      });
  }, []);

  // KPI Calculation (Total Revenue, Orders, AOV, etc.)
  const calculateKPIs = (data) => {
    const totalRevenue = data.reduce((acc, row) => acc + row.total_price, 0);
    const uniqueOrders = new Set(data.map(row => row.TransactionID)).size;
    const totalPizzas = data.reduce((acc, row) => acc + row.quantity, 0);
    const avgOrderValue = totalRevenue / uniqueOrders;

    setKpis({
      totalRevenue: `$${totalRevenue.toFixed(2)}`,
      avgOrderValue: `$${avgOrderValue.toFixed(2)}`,
      totalPizzas,
      totalOrders: uniqueOrders
    });
  };

  // Step 4 & 5: Load Data into Tableau Equivalent + Visualizations in Recharts
  const generateCharts = (data) => {
    const revenueByDate = {};
    const revenueByItemMap = {};
    const revenueByDay = {};
    const revenueByHour = {};

    data.forEach(row => {
      const date = row.order_date.toISOString().split('T')[0];
      revenueByDate[date] = (revenueByDate[date] || 0) + row.total_price;

      revenueByItemMap[row.item] = (revenueByItemMap[row.item] || 0) + row.total_price;

      const weekday = row.order_date.getDay();
      revenueByDay[weekday] = (revenueByDay[weekday] || 0) + row.total_price;

      const hour = row.order_time.getHours();
      revenueByHour[hour] = (revenueByHour[hour] || 0) + row.total_price;
    });

    setRevenueOverTime(Object.entries(revenueByDate).map(([date, value]) => ({ date, value })));
    setRevenueByItem(Object.entries(revenueByItemMap).map(([name, value]) => ({ name, value })));
    setRevenueByDay(Object.entries(revenueByDay).map(([day, value]) => ({ day, value })));
    setRevenueByHour(Object.entries(revenueByHour).map(([hour, value]) => ({ hour, value })));
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28'];

  // Step 6: Build UI as Dashboard (equivalent to Tableau layout)
  return (
    <div className="p-6 grid gap-6">
      <h1 className="text-3xl font-bold mb-4">PizzaPulse – Sales Revenue Analysis</h1>

      {/* KPI Section */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(kpis).map(([key, value]) => (
          <Card key={key}><CardContent>
            <p className="text-sm uppercase font-medium">{key.replace(/([A-Z])/g, ' $1')}</p>
            <p className="text-xl font-semibold">{value}</p>
          </CardContent></Card>
        ))}
      </div>

      {/* Step 7: Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Total Revenue Over Time */}
        <Card><CardContent><h2>Total Revenue Over Time</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={revenueOverTime}><XAxis dataKey="date" /><YAxis /><Tooltip /><Line type="monotone" dataKey="value" stroke="#8884d8" /></LineChart>
          </ResponsiveContainer></CardContent></Card>

        {/* Revenue by Item */}
        <Card><CardContent><h2>Revenue by Item</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={revenueByItem.slice(0, 5)}><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="value" fill="#00C49F" /></BarChart>
          </ResponsiveContainer></CardContent></Card>

        {/* Revenue by Day of Week */}
        <Card><CardContent><h2>Revenue by Day of Week</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={revenueByDay}><XAxis dataKey="day" /><YAxis /><Tooltip /><Bar dataKey="value" fill="#FFBB28" /></BarChart>
          </ResponsiveContainer></CardContent></Card>

        {/* Revenue by Time of Day */}
        <Card><CardContent><h2>Revenue by Time of Day</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={revenueByHour}><XAxis dataKey="hour" /><YAxis /><Tooltip /><Line type="monotone" dataKey="value" stroke="#FF8042" /></LineChart>
          </ResponsiveContainer></CardContent></Card>
      </div>

      {/* Step 8: Generate Predictive Insights or Export */}
      <div className="mt-6 text-center">
        <Button className="text-white bg-green-600 hover:bg-green-700">Export Dashboard</Button>
      </div>
    </div>
  );
};

// Step 9: Save and Share if needed (in Tableau it's File > Save As, here use frontend tools)

export default PizzaPulseApp;
