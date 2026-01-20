import React, { useState, useEffect } from 'react';
import { motion, useScroll, useMotionValueEvent } from 'framer-motion';

const Navbar = () => {
    const [hidden, setHidden] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    const { scrollY } = useScroll();

    useMotionValueEvent(scrollY, "change", (latest) => {
        const previous = scrollY.getPrevious();
        if (latest > previous && latest > 150) {
            setHidden(true);
        } else {
            setHidden(false);
        }

        if (latest > 50) {
            setScrolled(true);
        } else {
            setScrolled(false);
        }
    });

    return (
        <motion.nav
            className={`navbar ${scrolled ? 'scrolled' : ''}`}
            variants={{
                visible: { y: 0 },
                hidden: { y: "-100%" },
            }}
            animate={hidden ? "hidden" : "visible"}
            transition={{ duration: 0.35, ease: "easeInOut" }}
        >
            <a href="#" className="nav-logo">
                <img src="/assets/logo.svg" alt="HP Noble Logo" />
            </a>
            <div className="nav-links">
                <a href="#gallery" className="nav-item">Интерьер</a>
                <a href="#reservation" className="nav-item">Бронь</a>
                <a href="#contacts" className="nav-item">Контакты</a>
            </div>
            <a href="#reservation" className="mobile-menu-btn">Забронировать</a>
        </motion.nav>
    );
};

export default Navbar;


