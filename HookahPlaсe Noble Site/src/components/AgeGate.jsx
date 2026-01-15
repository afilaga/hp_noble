import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const AgeGate = ({ onVerify }) => {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const verified = localStorage.getItem('hp_noble_age_verified');
        if (verified !== 'true') {
            setIsVisible(true);
        } else {
            onVerify();
        }
    }, [onVerify]);

    const handleConfirm = () => {
        localStorage.setItem('hp_noble_age_verified', 'true');
        setIsVisible(false);
        onVerify();
    };

    const handleExit = () => {
        window.location.href = 'https://google.com';
    };

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    className="age-gate"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        backgroundColor: '#050505',
                        zIndex: 20000,
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        textAlign: 'center',
                        padding: '2rem'
                    }}
                >
                    <motion.div
                        className="age-gate-content"
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.2 }}
                        style={{
                            maxWidth: '500px',
                            width: '100%',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            gap: '1.5rem'
                        }}
                    >
                        <div className="age-gate-logo" style={{ marginBottom: '1rem' }}>
                            <svg viewBox="0 0 146.96 68.08" style={{ width: '80px', fill: '#C6A87C' }}>
                                <use href="/assets/logo.svg#_Слой_2"></use>
                            </svg>
                        </div>
                        <h2 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: '2.5rem', color: '#C6A87C', textTransform: 'uppercase' }}>Подтвердите возраст</h2>
                        <p style={{ fontSize: '1.2rem', color: '#E6E6E6' }}>Вам уже исполнилось 18 лет?</p>
                        <p style={{ fontSize: '0.9rem', color: '#888888', marginBottom: '1rem' }}>Сайт содержит информацию, не предназначенную для просмотра лицами младше 18 лет.</p>
                        
                        <div style={{ display: 'flex', gap: '1.5rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                            <button 
                                onClick={handleConfirm}
                                style={{
                                    padding: '1rem 2.5rem',
                                    border: '1px solid #C6A87C',
                                    color: '#C6A87C',
                                    backgroundColor: 'transparent',
                                    textTransform: 'uppercase',
                                    fontSize: '0.8rem',
                                    letterSpacing: '0.1em',
                                    cursor: 'pointer',
                                    transition: 'all 0.4s ease'
                                }}
                                onMouseEnter={(e) => { e.target.style.backgroundColor = '#C6A87C'; e.target.style.color = '#000'; }}
                                onMouseLeave={(e) => { e.target.style.backgroundColor = 'transparent'; e.target.style.color = '#C6A87C'; }}
                            >
                                Мне исполнилось 18
                            </button>
                            <button 
                                onClick={handleExit}
                                style={{
                                    padding: '1rem 2.5rem',
                                    border: '1px solid #888888',
                                    color: '#888888',
                                    backgroundColor: 'transparent',
                                    textTransform: 'uppercase',
                                    fontSize: '0.8rem',
                                    letterSpacing: '0.1em',
                                    cursor: 'pointer',
                                    transition: 'all 0.4s ease'
                                }}
                                onMouseEnter={(e) => { e.target.style.backgroundColor = '#888888'; e.target.style.color = '#000'; }}
                                onMouseLeave={(e) => { e.target.style.backgroundColor = 'transparent'; e.target.style.color = '#888888'; }}
                            >
                                Нет
                            </button>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default AgeGate;
