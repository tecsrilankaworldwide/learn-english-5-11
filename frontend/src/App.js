import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { 
  Globe, 
  MagnifyingGlass, 
  SpeakerHigh, 
  CaretDown,
  HandWaving,
  ShoppingCart,
  ForkKnife,
  MapPin,
  FirstAid,
  ChatCircle,
  Car,
  Bed,
  Spinner,
  MagnifyingGlassMinus
} from "@phosphor-icons/react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Icon mapping for categories
const categoryIcons = {
  HandWaving: HandWaving,
  ShoppingCart: ShoppingCart,
  ForkKnife: ForkKnife,
  MapPin: MapPin,
  FirstAid: FirstAid,
  ChatCircle: ChatCircle,
  Car: Car,
  Bed: Bed,
};

// Language Selector Component
const LanguageSelector = ({ languages, selectedLanguage, onSelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const selected = languages.find(l => l.code === selectedLanguage) || languages[0];
  
  return (
    <div className="language-dropdown">
      <button 
        data-testid="language-selector"
        className={`language-button ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="language-info">
          <span className="language-flag">{selected?.flag}</span>
          <div className="language-names">
            <div className="name">{selected?.name}</div>
            <div className="native">{selected?.native_name}</div>
          </div>
        </div>
        <CaretDown size={20} weight="bold" style={{ transform: isOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
      </button>
      
      {isOpen && (
        <div className="language-menu">
          {languages.map((lang) => (
            <button
              key={lang.code}
              data-testid={`language-option-${lang.code}`}
              className={`language-option ${lang.code === selectedLanguage ? 'selected' : ''}`}
              onClick={() => {
                onSelect(lang.code);
                setIsOpen(false);
              }}
            >
              <span className="language-flag">{lang.flag}</span>
              <div className="language-names">
                <div className="name">{lang.name}</div>
                <div className="native">{lang.native_name}</div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

// Category Card Component
const CategoryCard = ({ category, isActive, onClick }) => {
  const IconComponent = categoryIcons[category.icon] || Globe;
  
  return (
    <button
      data-testid={`category-${category.id}`}
      className={`category-card ${isActive ? 'active' : ''}`}
      onClick={onClick}
    >
      <IconComponent size={28} weight="duotone" className="category-icon" />
      <span className="category-name">{category.name}</span>
    </button>
  );
};

// Phrase Card Component
const PhraseCard = ({ phrase, languageName, onPlayEnglish, onPlayNative, loadingAudio }) => {
  return (
    <div className="phrase-card" data-testid={`phrase-card-${phrase.id}`}>
      <div className="phrase-text">
        <p className="english-phrase">{phrase.english}</p>
        <p className="native-phrase">{phrase.native}</p>
      </div>
      <div className="phrase-actions">
        <button
          data-testid={`play-english-${phrase.id}`}
          className={`audio-button english ${loadingAudio === `en-${phrase.id}` ? 'loading' : ''}`}
          onClick={() => onPlayEnglish(phrase)}
          disabled={loadingAudio === `en-${phrase.id}`}
        >
          {loadingAudio === `en-${phrase.id}` ? (
            <Spinner size={18} className="spinning" />
          ) : (
            <SpeakerHigh size={18} weight="fill" />
          )}
          English
        </button>
        <button
          data-testid={`play-native-${phrase.id}`}
          className={`audio-button native ${loadingAudio === `native-${phrase.id}` ? 'loading' : ''}`}
          onClick={() => onPlayNative(phrase)}
          disabled={loadingAudio === `native-${phrase.id}`}
        >
          {loadingAudio === `native-${phrase.id}` ? (
            <Spinner size={18} className="spinning" />
          ) : (
            <SpeakerHigh size={18} weight="fill" />
          )}
          {languageName}
        </button>
      </div>
    </div>
  );
};

// Toast Component
const Toast = ({ message, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);
  
  return <div className="toast">{message}</div>;
};

// Main App Component
function App() {
  const [languages, setLanguages] = useState([]);
  const [categories, setCategories] = useState([]);
  const [phrases, setPhrases] = useState([]);
  const [selectedLanguage, setSelectedLanguage] = useState("ja");
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadingAudio, setLoadingAudio] = useState(null);
  const [toast, setToast] = useState(null);

  // Fetch languages and categories on mount
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [langRes, catRes] = await Promise.all([
          axios.get(`${API}/languages`),
          axios.get(`${API}/categories`)
        ]);
        setLanguages(langRes.data.languages);
        setCategories(catRes.data.categories);
      } catch (error) {
        console.error("Failed to fetch initial data:", error);
        setToast("Failed to load data. Please refresh.");
      }
    };
    fetchInitialData();
  }, []);

  // Fetch phrases when language or category changes
  useEffect(() => {
    const fetchPhrases = async () => {
      setLoading(true);
      try {
        let url = selectedCategory 
          ? `${API}/phrases/${selectedCategory}?language_code=${selectedLanguage}`
          : `${API}/phrases?language_code=${selectedLanguage}`;
        
        const response = await axios.get(url);
        setPhrases(response.data.phrases);
      } catch (error) {
        console.error("Failed to fetch phrases:", error);
        setToast("Failed to load phrases.");
      } finally {
        setLoading(false);
      }
    };
    
    if (languages.length > 0) {
      fetchPhrases();
    }
  }, [selectedLanguage, selectedCategory, languages.length]);

  // Play audio using TTS
  const playAudio = useCallback(async (text, type, phraseId) => {
    const audioKey = `${type}-${phraseId}`;
    setLoadingAudio(audioKey);
    
    try {
      const response = await axios.post(`${API}/tts/generate`, {
        text: text,
        language_code: type === 'en' ? 'en' : selectedLanguage
      });
      
      if (response.data.audio_base64) {
        const audio = new Audio(`data:audio/mp3;base64,${response.data.audio_base64}`);
        audio.play();
      }
    } catch (error) {
      console.error("TTS Error:", error);
      setToast("Audio generation failed. Please try again.");
    } finally {
      setLoadingAudio(null);
    }
  }, [selectedLanguage]);

  const handlePlayEnglish = useCallback((phrase) => {
    playAudio(phrase.english, 'en', phrase.id);
  }, [playAudio]);

  const handlePlayNative = useCallback((phrase) => {
    playAudio(phrase.native, 'native', phrase.id);
  }, [playAudio]);

  // Filter phrases by search query
  const filteredPhrases = phrases.filter(phrase => 
    phrase.english.toLowerCase().includes(searchQuery.toLowerCase()) ||
    phrase.native.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const selectedLang = languages.find(l => l.code === selectedLanguage);

  return (
    <div className="App">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">
              <Globe size={24} weight="bold" />
            </div>
            <span className="logo-text">Travel Phrases</span>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-background" />
        <div className="hero-content">
          <div className="hero-text">
            <h1>Learn Essential Travel Phrases</h1>
            <p>Master common phrases in 14 languages with native pronunciation. Perfect for your next adventure abroad.</p>
          </div>
          <div className="hero-illustration">
            <img 
              src="https://static.prod-images.emergentagent.com/jobs/d830c768-d7c1-463b-8e61-1ac42dde8b9d/images/71626a3419a843ebaded07329ab95d8c7fe2c4d73be8b1d6a5791c5a2c1d7ccb.png" 
              alt="Travel illustration"
            />
          </div>
        </div>
      </section>

      {/* Language Selector & Search */}
      <div className="language-selector-wrapper">
        <div className="language-selector-content">
          <LanguageSelector 
            languages={languages}
            selectedLanguage={selectedLanguage}
            onSelect={setSelectedLanguage}
          />
          <div className="search-wrapper">
            <MagnifyingGlass size={20} className="search-icon" />
            <input
              data-testid="search-input"
              type="text"
              className="search-input"
              placeholder="Search phrases..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Categories */}
      <section className="categories-section">
        <h2 className="categories-title">Categories</h2>
        <div className="categories-grid">
          <button
            data-testid="category-all"
            className={`category-card ${selectedCategory === null ? 'active' : ''}`}
            onClick={() => setSelectedCategory(null)}
          >
            <Globe size={28} weight="duotone" className="category-icon" />
            <span className="category-name">All</span>
          </button>
          {categories.map(category => (
            <CategoryCard
              key={category.id}
              category={category}
              isActive={selectedCategory === category.id}
              onClick={() => setSelectedCategory(category.id)}
            />
          ))}
        </div>
      </section>

      {/* Phrases */}
      <section className="phrases-section">
        <div className="phrases-header">
          <h2 className="phrases-title">
            {selectedCategory 
              ? categories.find(c => c.id === selectedCategory)?.name || 'Phrases'
              : 'All Phrases'}
          </h2>
          <span className="phrases-count">{filteredPhrases.length} phrases</span>
        </div>

        {loading ? (
          <div className="loading-spinner">
            <div className="spinner" />
          </div>
        ) : filteredPhrases.length === 0 ? (
          <div className="empty-state">
            <MagnifyingGlassMinus size={64} />
            <p>No phrases found. Try a different search or category.</p>
          </div>
        ) : (
          <div className="phrases-grid">
            {filteredPhrases.map(phrase => (
              <PhraseCard
                key={phrase.id}
                phrase={phrase}
                languageName={selectedLang?.name || 'Native'}
                onPlayEnglish={handlePlayEnglish}
                onPlayNative={handlePlayNative}
                loadingAudio={loadingAudio}
              />
            ))}
          </div>
        )}
      </section>

      {/* Toast */}
      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </div>
  );
}

export default App;
