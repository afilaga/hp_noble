import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

const ReservationForm = () => {
    const [date, setDate] = useState('');
    const [time, setTime] = useState('');
    const [guests, setGuests] = useState(2);
    const [name, setName] = useState('');
    const [phone, setPhone] = useState('');
    const [loading, setLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [error, setError] = useState('');
    const [consent, setConsent] = useState(false);

    // Дефолтная дата — завтра
    useEffect(() => {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        setDate(tomorrow.toISOString().split('T')[0]);
    }, []);

    // Отправка брони (стол подбирается автоматически)
    const submitReservation = async () => {
        if (!name || !phone || !date || !time) {
            setError('Заполните все поля');
            return;
        }
        setLoading(true);
        setError('');
        try {
            const res = await fetch(`${API_BASE}/reservation/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name,
                    phone,
                    table_id: 'any', // Автоподбор стола на бэкенде
                    date,
                    time,
                    guests
                })
            });
            const data = await res.json();
            if (data.success) {
                setSubmitted(true);
            } else {
                setError(data.detail || data.error || 'Ошибка бронирования');
            }
        } catch (err) {
            setError('Ошибка сети. Попробуйте позже.');
        }
        setLoading(false);
    };

    // Генерация временных слотов
    const timeSlots = [];
    for (let h = 12; h <= 23; h++) {
        timeSlots.push(`${h.toString().padStart(2, '0')}:00`);
        timeSlots.push(`${h.toString().padStart(2, '0')}:30`);
    }

    const resetForm = () => {
        setSubmitted(false);
        setName('');
        setPhone('');
        setTime('');
        setGuests(2);
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        setDate(tomorrow.toISOString().split('T')[0]);
    };

    return (
        <section id="reservation" className="section reservation-section">
            <div className="container">
                <h2 className="section-title center">Бронирование</h2>

                <div className="reservation-card">
                    <AnimatePresence mode="wait">
                        {submitted ? (
                            <motion.div
                                key="success"
                                className="reservation-success"
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0 }}
                            >
                                <div className="success-icon">✓</div>
                                <h3>Бронирование принято</h3>
                                <p>
                                    Спасибо за бронирование! Будем ждать вас<br />
                                    <b>{new Date(date).toLocaleDateString('ru-RU')} в {time}</b><br />
                                    в HookahPlace Noble.
                                </p>
                                <button
                                    className="btn btn-primary"
                                    onClick={resetForm}
                                >
                                    Новое бронирование
                                </button>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="form"
                                className="reservation-step"
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                            >
                                <div className="form-grid">
                                    <div className="form-group">
                                        <label>Дата</label>
                                        <input
                                            type="date"
                                            value={date}
                                            onChange={(e) => setDate(e.target.value)}
                                            min={new Date().toISOString().split('T')[0]}
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label>Время</label>
                                        <select value={time} onChange={(e) => setTime(e.target.value)}>
                                            <option value="">Выберите время</option>
                                            {timeSlots.map(t => (
                                                <option key={t} value={t}>{t}</option>
                                            ))}
                                        </select>
                                    </div>

                                    <div className="form-group">
                                        <label>Гостей</label>
                                        <div className="guest-selector">
                                            <button
                                                type="button"
                                                onClick={() => setGuests(Math.max(1, guests - 1))}
                                                disabled={guests <= 1}
                                            >−</button>
                                            <span>{guests}</span>
                                            <button
                                                type="button"
                                                onClick={() => setGuests(Math.min(12, guests + 1))}
                                                disabled={guests >= 12}
                                            >+</button>
                                        </div>
                                    </div>
                                </div>

                                <div className="form-grid contact-form">
                                    <div className="form-group">
                                        <label>Имя</label>
                                        <input
                                            type="text"
                                            value={name}
                                            onChange={(e) => setName(e.target.value)}
                                            placeholder="Ваше имя"
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Телефон</label>
                                        <input
                                            type="tel"
                                            value={phone}
                                            onChange={(e) => setPhone(e.target.value)}
                                            placeholder="+7 (___) ___-__-__"
                                        />
                                    </div>
                                </div>

                                {error && <p className="error-msg">{error}</p>}

                                <div className="form-group checkbox-group">
                                    <input
                                        type="checkbox"
                                        id="consent"
                                        checked={consent}
                                        onChange={(e) => setConsent(e.target.checked)}
                                    />
                                    <label htmlFor="consent">
                                        Я согласен на обработку персональных данных
                                    </label>
                                </div>

                                <button
                                    className="btn btn-primary"
                                    onClick={submitReservation}
                                    disabled={!date || !time || !name || !phone || !consent || loading}
                                >
                                    {loading ? 'Отправка...' : 'Забронировать'}
                                </button>

                                <div className="telegram-bot-link">
                                    <p>или забронируйте через</p>
                                    <a href="https://t.me/hp_noble_bot" target="_blank" rel="noopener noreferrer" className="btn btn-telegram">
                                        <span className="telegram-icon">✈</span> Telegram бот @hp_noble_bot
                                    </a>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </section>
    );
};

export default ReservationForm;
