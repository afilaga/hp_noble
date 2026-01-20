import React from 'react';
import { motion } from 'framer-motion';

const Marquee = () => {
    return (
        <motion.div 
            className="marquee-strip"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1 }}
        >
            <div className="marquee-content">
                {Array(8).fill(null).map((_, i) => (
                    <React.Fragment key={i}>
                        <span>HOOKAH PLACE</span>
                        <span className="separator">-</span>
                        <span>NOBLE</span>
                        <span className="separator">-</span>
                        <span>SOCHI</span>
                        <span className="separator">-</span>
                    </React.Fragment>
                ))}
            </div>
        </motion.div>
    );
};

export default Marquee;
