import React from 'react';
import { motion } from 'framer-motion';
import { LiquidMetal } from '@paper-design/shaders-react';
import LiquidBackground from './LiquidBackground';

const Hero = () => {
    return (
        <section className="hero">
            <LiquidBackground />
            <div className="hero-content">
                <div className="hero-logo-container">
                    <LiquidMetal
                        width={window.innerWidth > 768 ? 400 : 250}
                        height={window.innerWidth > 768 ? 160 : 100}
                        speed={0.6}
                        image="/assets/logo-noble.webp"
                        colorBack="#ffffff00"
                        colorTint="#ffd900"
                        shape={undefined}
                        repetition={1.82}
                        softness={0.75}
                        shiftRed={0.3}
                        shiftBlue={0.3}
                        distortion={0.53}
                        contour={0.79}
                        angle={70}
                        scale={0.6}
                        fit="contain"
                    />
                </div>

                <motion.p
                    className="hero-subtitle"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 1.2 }}
                >
                    Премиальный лаунж в сердце Сочи
                </motion.p>

                <motion.div
                    className="hero-cta"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 1.4 }}
                >
                    <a href="#reservation" className="btn btn-primary">Забронировать</a>
                </motion.div>
            </div>
            <div className="hero-overlay"></div>
            <div className="smoke-container"></div>
        </section>
    );
};

export default Hero;
