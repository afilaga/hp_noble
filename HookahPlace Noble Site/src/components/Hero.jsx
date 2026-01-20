import React from 'react';
import { motion } from 'framer-motion';
import { LiquidMetal } from '@paper-design/shaders-react';
import LiquidBackground from './LiquidBackground';

const Hero = () => {
    return (
        <section className="hero">
            <LiquidBackground />
            <div className="hero-content">
                <motion.div
                    className="hero-logo-container"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{
                        duration: 1.2,
                        ease: [0.2, 1, 0.3, 1]
                    }}
                >
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
                </motion.div>

                <motion.p
                    className="hero-subtitle"
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{
                        duration: 1,
                        delay: 0.8,
                        ease: [0.2, 1, 0.3, 1]
                    }}
                >
                    Премиальный лаунж в сердце Сочи
                </motion.p>

                <motion.div
                    className="hero-cta"
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{
                        duration: 1,
                        delay: 1,
                        ease: [0.2, 1, 0.3, 1]
                    }}
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
