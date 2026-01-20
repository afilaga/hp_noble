import React from 'react';
import { motion } from 'framer-motion';

const Contacts = () => {
    return (
        <section id="contacts" className="section contacts">
            <div className="container">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8 }}
                >
                    <h2 className="section-title center">Контакты</h2>
                    <div className="contacts-grid">
                        <div className="contact-card">
                            <h3>Адрес</h3>
                            <a href="https://yandex.ru/maps/-/CLdGvH7M" target="_blank" rel="noopener noreferrer" className="contact-link">
                                Сочи, ул. Воровского, 35А<br />микрорайон Центральный
                            </a>
                        </div>
                        <div className="contact-card">
                            <h3>Телефон</h3>
                            <a href="tel:+79182799696" className="contact-link">+7 (918) 279-96-96</a>
                        </div>
                        <div className="contact-card">
                            <h3>Telegram</h3>
                            <a href="https://t.me/hp_noble_bot" target="_blank" rel="noopener noreferrer" className="contact-link">@hp_noble_bot</a>
                        </div>
                        <div className="contact-card">
                            <h3>Время работы</h3>
                            <p>Ежедневно<br />12:00 — 02:00</p>
                        </div>
                    </div>
                </motion.div>
            </div>
        </section>
    );
};

export default Contacts;

