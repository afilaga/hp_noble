import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const PrivacyPolicyModal = ({ isOpen, onClose }) => {
    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <motion.div
                className="modal-overlay"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={onClose}
                style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    background: 'rgba(0, 0, 0, 0.8)',
                    backdropFilter: 'blur(5px)',
                    zIndex: 10000,
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    padding: '1rem'
                }}
            >
                <motion.div
                    className="modal-content"
                    initial={{ y: 50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: 50, opacity: 0 }}
                    onClick={(e) => e.stopPropagation()}
                    style={{
                        background: '#121212',
                        border: '1px solid #333',
                        padding: '2rem',
                        maxWidth: '800px',
                        width: '100%',
                        maxHeight: '90vh',
                        overflowY: 'auto',
                        color: '#E6E6E6',
                        fontFamily: 'Manrope, sans-serif',
                        position: 'relative'
                    }}
                >
                    <button 
                        onClick={onClose}
                        style={{
                            position: 'absolute',
                            top: '1rem',
                            right: '1rem',
                            background: 'transparent',
                            border: 'none',
                            color: '#888',
                            fontSize: '1.5rem',
                            cursor: 'pointer'
                        }}
                    >
                        &times;
                    </button>

                    <h2 style={{ fontFamily: 'Cormorant Garamond, serif', color: '#C6A87C', marginBottom: '1.5rem' }}>Согласие на обработку персональных данных</h2>
                    
                    <div style={{ fontSize: '0.9rem', lineHeight: '1.6', color: '#ccc' }}>
                        <p style={{ marginBottom: '1rem' }}>
                            Я, свободно, своей волей и в своем интересе даю конкретное, информированное и сознательное согласие <strong>Индивидуальному предпринимателю Погосян Закару Вагановичу</strong> (ИНН 232016373278) (далее – Оператор), на обработку моих персональных данных на следующих условиях:
                        </p>

                        <h3 style={{ color: '#fff', margin: '1rem 0 0.5rem' }}>1. Цель обработки данных</h3>
                        <p style={{ marginBottom: '1rem' }}>
                            Обеспечение возможности бронирования столов, обратной связи с клиентом, информирования о статусе заказа/брони, предоставления сервисных услуг Hookah Place Noble.
                        </p>

                        <h3 style={{ color: '#fff', margin: '1rem 0 0.5rem' }}>2. Перечень персональных данных</h3>
                        <p style={{ marginBottom: '1rem' }}>
                            Согласие дается на обработку следующих персональных данных, не являющихся специальными или биометрическими:
                        </p>
                        <ul style={{ listStyle: 'disc', paddingLeft: '1.5rem', marginBottom: '1rem' }}>
                            <li>Фамилия, имя, отчество (при наличии);</li>
                            <li>Номера контактных телефонов;</li>
                            <li>Пользовательские данные (сведения о местоположении, тип и версия ОС, тип и версия браузера, тип устройства и разрешение его экрана, источник, откуда пришел на сайт пользователь, с какого сайта или по какой рекламе, язык ОС и браузера, какие страницы открывает и на какие кнопки нажимает пользователь, ip-адрес).</li>
                        </ul>

                        <h3 style={{ color: '#fff', margin: '1rem 0 0.5rem' }}>3. Действия с данными</h3>
                        <p style={{ marginBottom: '1rem' }}>
                            Оператор вправе совершать следующие действия (операции) с персональными данными: сбор, запись, систематизация, накопление, хранение, уточнение (обновление, изменение), извлечение, использование, передача (предоставление, доступ) третьим лицам (в том числе партнерам, обеспечивающим функционирование сервисов бронирования), обезличивание, блокирование, удаление, уничтожение персональных данных.
                        </p>
                        <p style={{ marginBottom: '1rem' }}>
                            Обработка персональных данных может осуществляться как с использованием средств автоматизации, так и без их использования.
                        </p>

                        <h3 style={{ color: '#fff', margin: '1rem 0 0.5rem' }}>4. Срок действия согласия</h3>
                        <p style={{ marginBottom: '1rem' }}>
                            Настоящее согласие действует бессрочно с момента предоставления данных и может быть отозвано мной в любой момент путем направления письменного заявления Оператору.
                        </p>
                        
                        <p style={{ fontSize: '0.8rem', color: '#888', marginTop: '2rem' }}>
                            Настоящим я подтверждаю, что являюсь субъектом предоставляемых персональных данных, а также подтверждаю достоверность предоставляемых данных.
                        </p>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
};

export default PrivacyPolicyModal;
