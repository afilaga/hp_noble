import React, { useState } from 'react';
import PrivacyPolicyModal from './PrivacyPolicyModal';

const Footer = () => {
    const [isPolicyOpen, setPolicyOpen] = useState(false);

    return (
        <>
            <footer className="footer">
                <div className="container">
                    <div className="footer-inner">
                        <div className="footer-top">
                            <div className="footer-logo">
                                <img src="/assets/logo.svg" alt="HP Noble Logo" style={{ height: '50px', filter: 'invert(1)' }} />
                            </div>
                            <div className="footer-socials">
                                <a 
                                    href="#" 
                                    className="social-icon-insta" 
                                    title="Meta Platforms Inc. признана экстремистской организацией и запрещена на территории РФ"
                                >
                                    {/* Abstract Camera Icon */}
                                    <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round">
                                        <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                                        <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                                        <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
                                    </svg>
                                    <span className="asterisk">*</span>
                                </a>
                                <a href="https://t.me/hp_noble_bot" target="_blank" rel="noopener noreferrer">Telegram</a>
                            </div>
                        </div>
                        
                        <div className="footer-bottom">
                            <div className="legal-info">
                                <p>ИП Погосян Закар Ваганович</p>
                                <p>ИНН 232016373278</p>
                                <p className="franchise-info">
                                    Официальный сайт франшизы: <a href="https://hookahplace.ru/" target="_blank" rel="noopener noreferrer">hookahplace.ru</a>
                                </p>
                            </div>
                            <button 
                                className="policy-link" 
                                onClick={() => setPolicyOpen(true)}
                            >
                                Согласие на обработку персональных данных
                            </button>
                            <div className="footer-copy">© 2026 Hookah Place Noble.</div>
                            <p className="meta-disclaimer">
                                * Meta Platforms Inc. признана экстремистской организацией и запрещена на территории РФ
                            </p>
                        </div>
                    </div>
                </div>
            </footer>
            
            <PrivacyPolicyModal 
                isOpen={isPolicyOpen} 
                onClose={() => setPolicyOpen(false)} 
            />

            <style>{`
                .footer-inner {
                    display: flex;
                    flex-direction: column;
                    gap: 2rem;
                }
                .footer-top {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .footer-socials {
                    display: flex;
                    align-items: center;
                    gap: 1.5rem;
                }
                .social-icon-insta {
                    display: flex;
                    align-items: center;
                    color: inherit;
                    position: relative;
                }
                .social-icon-insta:hover {
                    color: #C6A87C;
                }
                .asterisk {
                    font-size: 0.8rem;
                    margin-left: 2px;
                    vertical-align: super;
                }
                .footer-bottom {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                    gap: 0.5rem;
                    border-top: 1px solid #333;
                    padding-top: 2rem;
                    font-size: 0.8rem;
                    color: #666;
                }
                .legal-info p {
                    margin: 0;
                    line-height: 1.4;
                }
                .franchise-info {
                    margin-top: 0.5rem !important;
                    font-size: 0.75rem;
                }
                .franchise-info a {
                    color: #888;
                    text-decoration: underline;
                }
                .franchise-info a:hover {
                    color: #C6A87C;
                }
                .policy-link {
                    background: none;
                    border: none;
                    color: #888;
                    text-decoration: underline;
                    cursor: pointer;
                    font-family: inherit;
                    font-size: 0.8rem;
                    padding: 0;
                    margin: 0.5rem 0;
                    transition: color 0.3s;
                }
                .policy-link:hover {
                    color: #C6A87C;
                }
                .meta-disclaimer {
                    font-size: 0.6rem;
                    opacity: 0.5;
                    margin-top: 1rem;
                    max-width: 80%;
                }
                @media (max-width: 768px) {
                    .footer-top {
                        flex-direction: column;
                        gap: 1.5rem;
                    }
                }
            `}</style>
        </>
    );
};

export default Footer;
