import React from 'react';

const Navbar = () => {
    return (
        <nav className="navbar">
            <a href="#" className="nav-logo">
                <img src="/assets/logo.svg" alt="HP Noble Logo" />
            </a>
            <div className="nav-links">
                <a href="#gallery" className="nav-item">Интерьер</a>
                <a href="#reservation" className="nav-item">Бронь</a>
                <a href="#contacts" className="nav-item">Контакты</a>
            </div>
            <a href="#reservation" className="mobile-menu-btn">Забронировать</a>
        </nav>
    );
};

export default Navbar;


