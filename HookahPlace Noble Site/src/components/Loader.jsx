import React, { useEffect } from 'react';
import { motion } from 'framer-motion';

const Loader = ({ setLoading }) => {
    useEffect(() => {
        // Simulate loading time (assets, fonts, etc.)
        const timer = setTimeout(() => {
            setLoading(false);
        }, 2500);
        return () => clearTimeout(timer);
    }, [setLoading]);

    return (
        <motion.div
            className="loader"
            exit={{ y: '-100%', transition: { duration: 0.8, ease: [0.19, 1, 0.22, 1] } }}
        >
            <div className="loader-logo">
                <svg viewBox="0 0 146.96 68.08" className="logo-svg">
                    <use href="/assets/logo.svg#_Слой_2"></use>
                </svg>
            </div>
        </motion.div>
    );
};

export default Loader;
