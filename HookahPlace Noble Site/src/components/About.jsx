import React from 'react';
import { motion } from 'framer-motion';

const About = () => {
    return (
        <section id="about" className="section about">
            <div className="container">
                <div className="about-grid">
                    <motion.div
                        className="about-text"
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8 }}
                    >
                        <h2 className="section-title">Философия</h2>
                        <p className="text-body">
                            Мы создали пространство, где время замедляется. Hookah Place Noble — это не просто кальянная, это место силы.
                            Благородные материалы, приглушенный свет и безупречный сервис создают атмосферу, достойную вашего вечера.
                        </p>
                        <p className="text-body mt-2">
                            Лучшие мастера индустрии. Редкие табаки. Авторская чайная карта и коктейли, которые идеально дополняют вкус.
                        </p>
                    </motion.div>
                    <motion.div
                        className="about-visual"
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                    >
                        <div className="image-placeholder gradient-box"></div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
};

export default About;
