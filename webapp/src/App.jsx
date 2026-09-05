import { useState, useEffect } from 'react';
import { Search, SlidersHorizontal, Store, Gift, ChevronUp, Loader2 } from 'lucide-react';
import './index.css';

// Addresses for TON Collections
const NUMBERS_COLLECTION = 'EQAOQdwdw8kGftJCSFgOErM1mBjYPe4DBPq8-AhF6vr9si5N';

// Fallback Mock Data for Gifts (since they are individual NFTs and don't have a single collection)
const FALLBACK_GIFTS = [
  { id: '1', metadata: { name: 'Серце', description: '15 зірок', image: 'https://em-content.zobj.net/source/apple/391/heart-with-ribbon_1f49d.png' }, price: 15, bg: 'bg-dark' },
  { id: '2', metadata: { name: 'Ведмедик', description: '15 зірок', image: 'https://em-content.zobj.net/source/apple/391/teddy-bear_1f9f8.png' }, price: 15, bg: 'bg-dark' },
  { id: '3', metadata: { name: 'Подарунок', description: '25 зірок', image: 'https://em-content.zobj.net/source/apple/391/wrapped-present_1f381.png' }, price: 25, bg: 'bg-dark' },
  { id: '4', metadata: { name: 'Троянда', description: '25 зірок', image: 'https://em-content.zobj.net/source/apple/391/rose_1f339.png' }, price: 25, bg: 'bg-dark' },
  { id: '5', metadata: { name: 'Торт', description: '50 зірок', image: 'https://em-content.zobj.net/source/apple/391/birthday-cake_1f382.png' }, price: 50, bg: 'bg-dark' },
  { id: '6', metadata: { name: 'Ракета', description: '50 зірок', image: 'https://em-content.zobj.net/source/apple/391/rocket_1f680.png' }, price: 50, bg: 'bg-dark' },
];

const FALLBACK_USERNAMES = [
  { id: 'u1', metadata: { name: '@upujo', description: 'upujo.t.me' }, price: 5, bg: 'bg-dark' },
  { id: 'u2', metadata: { name: '@gupvo', description: 'gupvo.t.me' }, price: 5, bg: 'bg-dark' },
  { id: 'u3', metadata: { name: '@lumi', description: 'lumi.t.me' }, price: 1500, bg: 'bg-dark' }
];

function App() {
  const [activeTab, setActiveTab] = useState('gifts');
  const [tg, setTg] = useState(null);
  
  // Dynamic Data States
  const [numbersData, setNumbersData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (window.Telegram && window.Telegram.WebApp) {
      const webapp = window.Telegram.WebApp;
      webapp.ready();
      webapp.expand();
      webapp.setHeaderColor('#0e1013');
      setTg(webapp);
    }
    
    // Fetch data from TonAPI
    const fetchTonApiData = async () => {
      setLoading(true);
      try {
        const numRes = await fetch(`https://tonapi.io/v2/nfts/collections/${NUMBERS_COLLECTION}/items?limit=20`);
        const numJson = await numRes.json();
        if (numJson.nft_items) {
          setNumbersData(numJson.nft_items);
        }
      } catch (error) {
        console.error("Failed to fetch from TonAPI", error);
      }
      setLoading(false);
    };

    fetchTonApiData();
  }, []);

  const handleBuy = (item, type) => {
    const itemName = item.metadata?.name || item.name;
    const itemPrice = item.price || 150; // default for demo
    
    if (tg) {
      const data = JSON.stringify({ action: 'buy_fragment', type, item: { name: itemName, price: itemPrice } });
      tg.sendData(data);
    } else {
      alert(`Купівля: ${itemName} за ${itemPrice} ₴`);
    }
  };

  return (
    <div className="app-container">
      {/* Banner */}
      <div className="banner">
        <h1>Купівля<br/>подарунків</h1>
        <p>NFT • юзернейми • номери</p>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <div className={`tab ${activeTab === 'gifts' ? 'active' : ''}`} onClick={() => setActiveTab('gifts')}>Подарунки</div>
        <div className={`tab ${activeTab === 'usernames' ? 'active' : ''}`} onClick={() => setActiveTab('usernames')}>Юзернейми</div>
        <div className={`tab ${activeTab === 'numbers' ? 'active' : ''}`} onClick={() => setActiveTab('numbers')}>Номера</div>
      </div>

      {/* Search & Filters */}
      <div className="search-container">
        <div className="search-input-wrapper">
          <Search size={20} color="var(--hint-color)" />
          <input type="text" placeholder="Пошук..." />
        </div>
        <button className="filter-btn">
          <SlidersHorizontal size={20} />
        </button>
      </div>

      {activeTab === 'gifts' && (
        <div className="filters-row">
          <div className="filter-chip">🎁 Колекція <ChevronUp size={14}/></div>
          <div className="filter-chip">💎 Модель <ChevronUp size={14}/></div>
          <div className="filter-chip">🎨 Фон <ChevronUp size={14}/></div>
        </div>
      )}

      {/* Loading State */}
      {loading && activeTab === 'numbers' && (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
          <Loader2 className="animate-spin" color="var(--button-color)" size={32} />
        </div>
      )}

      {/* Grid Content */}
      <div className="grid">
        {activeTab === 'gifts' && FALLBACK_GIFTS.map(gift => (
          <div className="card" key={gift.id}>
            <div className={`card-image-container ${gift.bg}`}>
              <div className="pattern-overlay"></div>
              <img src={gift.metadata.image} alt={gift.metadata.name} className="card-emoji-img" />
            </div>
            <div className="card-title">{gift.metadata.name}</div>
            <div className="card-subtitle">{gift.metadata.description}</div>
            <div className="card-actions">
              <button className="btn-price" onClick={() => handleBuy(gift, 'gift')}>від {gift.price} ₴</button>
              <button className="btn-cart"><Store size={18} /></button>
            </div>
          </div>
        ))}

        {activeTab === 'usernames' && FALLBACK_USERNAMES.map(user => (
          <div className="card" key={user.id}>
            <div className={`card-image-container ${user.bg}`}>
              <div className="pattern-overlay"></div>
              <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f48e/512.webp" alt="diamond" className="card-emoji-img-small" />
              <span className="card-username">{user.metadata.name}</span>
            </div>
            <div className="card-title">{user.metadata.name}</div>
            <div className="card-subtitle">{user.metadata.description}</div>
            <div className="card-actions">
              <button className="btn-price" onClick={() => handleBuy(user, 'username')}>від {user.price} ₴</button>
              <button className="btn-cart"><Store size={18} /></button>
            </div>
          </div>
        ))}

        {activeTab === 'numbers' && !loading && numbersData.map((num, i) => {
          const imgUrl = num.previews?.[1]?.url || num.metadata?.image || "https://fonts.gstatic.com/s/e/notoemoji/latest/260e/512.webp";
          return (
            <div className="card" key={num.address}>
              <div className="card-image-container bg-blue">
                <div className="pattern-overlay"></div>
                <img src={imgUrl} alt="number" className="card-emoji-full" style={{opacity: 1}} />
              </div>
              <div className="card-title">{num.metadata?.name || "Anonymous Number"}</div>
              <div className="card-subtitle">TonAPI Data</div>
              <div className="card-actions">
                <button className="btn-price" onClick={() => handleBuy(num, 'number')}>від {100 + i * 50} ₴</button>
                <button className="btn-cart"><Store size={18} /></button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Bottom Navigation */}
      <div className="bottom-nav">
        <div className="nav-item active">
          <Store size={22} />
          <span className="nav-text">Каталог</span>
        </div>
        <div className="nav-item">
          <Gift size={22} />
          <span className="nav-text">Мої покупки</span>
        </div>
      </div>
    </div>
  );
}

export default App;
