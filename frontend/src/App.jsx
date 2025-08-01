import { useEffect, useState, useRef } from 'react';
import './App.css';
import dark from './assets/dark.png';
import light from './assets/light.png';
import show from './assets/show.png';
import hide from './assets/hide.png';
import trash from './assets/trash.png';
import { BACKEND_URL } from "../config";

function App() {
  const [pages, setPages] = useState([]);
  const [selectedPage, setSelectedPage] = useState(null);
  const [blocks, setBlocks] = useState([]);
  const [newPageTitle, setNewPageTitle] = useState('');
  const [darkMode, setDarkMode] = useState(false);
  const [user, setUser] = useState(null);
  const [authMode, setAuthMode] = useState('login');
  const [authUsername, setAuthUsername] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [levelUp, setLevelUp] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const prevLevel = useRef(null);
  const titleRef = useRef(null);
  const editableRefs = useRef({});

  const site = BACKEND_URL;

  const triggerLevelUpAnimation = () => {
    setLevelUp(true);
    setTimeout(() => setLevelUp(false), 1000);
  };

  useEffect(() => {
    fetch(`${site}/user/stats`, { method: 'GET', credentials: 'include' })
      .then(res => (res.ok ? res.json() : null))
      .then(data => {
        if (data?.username) {
          setUser(data);
          fetchPages();
        }
      });
  }, []);

  const fetchPages = () => {
    fetch(`${site}/pages`, { credentials: 'include' })
      .then(res => res.json())
      .then(pages => {
        setPages(pages);
        if (pages.length > 0) {
          selectPage(pages[0]);
        }
      });
  };

  const fetchStats = () => {
    fetch(`${site}/user/stats`, { credentials: 'include' })
      .then(res => res.json())
      .then(stats => {
        if (stats && stats.level !== undefined) {
          setUser(stats);
        }
        if (prevLevel.current !== null && stats.level > prevLevel.current) {
            triggerLevelUpAnimation();
          }
        prevLevel.current = stats.level;
      });
  };

  useEffect(() => {
    if (darkMode) {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
  }, [darkMode]);

  const selectPage = (page) => {
    setSelectedPage(page);
    fetch(`${site}/pages/${page.id}/blocks`, { credentials: 'include' })
      .then(res => res.json())
      .then(setBlocks);
  };

  const createPage = () => {
    fetch(`${site}/pages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: newPageTitle }),
      credentials: 'include',
    })
      .then(res => res.json())
      .then(page => {
        setPages([...pages, page]);
        setNewPageTitle('');
      });
  };

  const renamePage = (pageId, newTitle) => {
    fetch(`${site}/pages/${pageId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: newTitle }),
      credentials: 'include',
    })
      .then(res => res.json())
      .then(updated => {
        setPages(pages.map(p => (p.id === pageId ? updated : p)));
        if (selectedPage?.id === pageId) {
          setSelectedPage(updated);
        }
      });
  };

  const deletePage = (pageId) => {
    fetch(`${site}/pages/${pageId}`, { method: 'DELETE', credentials: 'include' }).then(() => {
      setPages(pages.filter(p => p.id !== pageId));
      if (selectedPage?.id === pageId) {
        setSelectedPage(null);
        setBlocks([]);
      }
    });
  };

  const addBlock = (type = 'text') => {
    if (!selectedPage) return;
    fetch(`${site}/blocks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        page_id: selectedPage.id,
        type: type,
        content: type === 'todo' ? { checked: false, text: '' } : '',
        order_index: blocks.length,
      }),
      credentials: 'include',
    })
      .then(res => res.json())
      .then(block => setBlocks([...blocks, block]));
  };

  const updateBlock = (blockId, content) => {
    const wordCount = countWords(typeof content === 'string' ? content : content.text);
    
    fetch(`${site}/blocks/${blockId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        content,
        word_count: wordCount // Send explicit word count
      }),
      credentials: 'include',
    })
      .then(res => res.json())
      .then(updated => {
        setBlocks(blocks.map(b => (b.id === blockId ? updated : b)));
        fetchStats(); // Refresh stats
      });
  };

  const deleteBlock = (blockId) => {
    fetch(`${site}/blocks/${blockId}`, { method: 'DELETE', credentials: 'include' }).then(() => {
      setBlocks(blocks.filter(b => b.id !== blockId));
    });
  };

  const login = () => {
    fetch(`${site}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username: authUsername, password: authPassword }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          alert(data.error);
        } else {
          fetch(`${site}/user/stats`, { credentials: 'include' })
            .then(res => res.json())
            .then(stats => {
              if (stats) {
                setUser(stats);
                fetchPages();
              } else {
                console.error('Stats fetch failed:', stats);
                alert('Login session failed. Check cookies.');
              }
            });
        }
      })
      .catch(err => {
        console.error('Login error:', err);
      });
  };

  const register = () => {
    fetch(`${site}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: authUsername, password: authPassword }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.message) {
          alert('Registration successful. Please login.');
          setAuthMode('login');
        } else {
          alert(data.error || 'Registration failed');
        }
      });
  };

  const logout = () => {
    fetch(`${site}/logout`, {
      method: 'POST',
      credentials: 'include',
    }).then(() => {
      setUser(null);
      setPages([]);
      setSelectedPage(null);
      setBlocks([]);
      window.location.reload();
    });
  };

  const countWords = (text) => {
    if (!text) return 0;
    // Replace all types of spaces and newlines with single space
    return text.replace(/[\n\r\t]/g, ' ')
              .replace(/\s+/g, ' ')
              .trim()
              .split(' ')
              .filter(word => word.length > 0)
              .length;
  };

  return (
    <div className="app-container">
      {!user ? (
        <div className="auth-box">
          <h2>{authMode === 'login' ? 'Login' : 'Register'}</h2>
          <input
            value={authUsername}
            onChange={(e) => setAuthUsername(e.target.value)}
            placeholder="Username"
            autoComplete="username"
            required
          />
          <div className="password-field">
            <input
              type={showPassword ? 'text' : 'password'}
              value={authPassword}
              onChange={(e) => setAuthPassword(e.target.value)}
              placeholder="Password"
              autoComplete={authMode === 'login' ? 'current-password' : 'new-password'}
              required
            />
            <button
              type="button"
              className="toggle-password"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <img src={hide} alt="hide" /> : <img src={show} alt="show" />}
            </button>
          </div>
          <button onClick={authMode === 'login' ? login : register}>
            {authMode === 'login' ? 'Login' : 'Register'}
          </button>
          <p>
            {authMode === 'login' ? (
              <>
                Don't have an account?{' '}
                <button onClick={() => setAuthMode('register')}>Register</button>
              </>
            ) : (
              <>
                Already have an account?{' '}
                <button onClick={() => setAuthMode('login')}>Login</button>
              </>
            )}
          </p>
        </div>
      ) : (
        <>
          <div className="sidebar">
            <h3
              className="clickable-header"
              onClick={() => setSelectedPage(null)}
              style={{ userSelect: 'none' }}
            >
              Home
            </h3>
            <input
              value={newPageTitle}
              onChange={(e) => setNewPageTitle(e.target.value)}
              placeholder="New page title"
              required
            />
            <button
              onClick={() => {
                if (newPageTitle.trim()) {
                  createPage();
                } else {
                  alert('Page title is required.');
                }
              }}
            >
              Add Page
            </button>

            <div className="page-list-scroll">
              {pages.map((page) => (
                <div
                  key={page.id}
                  className={`page-item ${selectedPage?.id === page.id ? 'selected' : ''}`}
                  onClick={() => selectPage(page)}
                >
                  <span style={{ whiteSpace: 'pre-wrap' }}>{page.title}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deletePage(page.id);
                    }}
                    className="trash"
                  >
                    <img src={trash} />
                  </button>
                </div>
              ))}
            </div>

            <button onClick={() => setDarkMode(!darkMode)} className="toggle-mode">
              Toggle {darkMode ? 'Light' : 'Dark'} Mode
            </button>

            {user?.username && (
              <div className="auth-info">
                Logged in as <strong>{user.username}</strong>
                <br />
                Level {user.level}
                {levelUp && <div className="level-up-popup">🎉 Level Up! 🎉</div>}
                <div className="progress-container">
                  <progress
                    value={user.progress}
                    max={user.next_level_words}
                    className="custom-progress"
                  />
                  <div className="progress-text">
                    {user.progress} / {user.next_level_words} words
                  </div>
                </div>
                <div className="info-footer">
                  <p>If you delete words, you must save then continue to update word count.</p>
                  <button className="logout" onClick={logout}>
                    Logout
                  </button>
                </div>
              </div>
            )}
          </div>

          <div className="editor">
            {selectedPage ? (
              <>
                <div
                  ref={titleRef}
                  contentEditable
                  suppressContentEditableWarning={true}
                  onBlur={(e) => {
                    // Replace <div> and <br> with \n before saving (preserve \n)
                    const html = e.currentTarget.innerHTML;
                    const textWithNewlines = html
                      .replace(/<div>/g, '\n')
                      .replace(/<\/div>/g, '')
                      .replace(/<br\s*\/?>/g, '\n');
                    renamePage(selectedPage.id, textWithNewlines)
                  }}
                  dangerouslySetInnerHTML={{
                    // Convert stored \n to HTML line breaks for display
                    __html: selectedPage.title.replace(/\n/g, '<br>'),
                  }}
                  style={{ whiteSpace: 'pre-wrap' }} // Preserves visual line breaks
                  data-placeholder="Page title."
                  className="page-title content-editable"
                />
                {blocks.map((block) => (
                  <div
                    key={block.id}
                    className={`block-row ${block.type === 'todo' ? 'todo-block' : ''}`}
                  >
                    {block.type === 'text' ? (
                      <div
                        contentEditable
                        suppressContentEditableWarning
                        ref={(el) => (editableRefs.current[block.id] = el)}
                        onBlur={(e) => {
                          const html = e.currentTarget.innerHTML;
                          const textWithNewlines = html
                            .replace(/<div>/g, '\n')
                            .replace(/<\/div>/g, '')
                            .replace(/<br\s*\/?>/g, '\n')
                            .replace(/&nbsp;/g, ' ');
                          updateBlock(block.id, textWithNewlines);
                        }}
                        dangerouslySetInnerHTML={{
                          __html: block.content.replace(/\n/g, '<br>'),
                        }}
                        style={{ whiteSpace: 'pre-wrap' }}
                        data-placeholder="Start typing..."
                        className="block-editable content-editable"
                      />
                    ) : (
                      <>
                        <input
                          type="checkbox"
                          checked={block.content.checked}
                          onChange={() =>
                            updateBlock(block.id, {
                              ...block.content,
                              checked: !block.content.checked,
                            })
                          }
                        />
                        <div
                          contentEditable
                          suppressContentEditableWarning
                          ref={(el) => {
                            if (el) {
                              editableRefs.current[block.id] = el;
                              el.textContent = block.content.text;
                            }
                          }}
                          onBlur={(e) => {
                            updateBlock(block.id, {
                              ...block.content,
                              text: e.currentTarget.textContent,
                            });
                          }}
                          data-placeholder="TODO"
                          className="block-editable content-editable"
                          style={{
                            textDecoration: block.content.checked ? 'line-through' : 'none',
                            whiteSpace: 'pre-wrap'
                          }}
                        />
                      </>
                    )}
                    <button onClick={() => deleteBlock(block.id)}
                      className='trash'>
                      <img src={trash}></img>
                    </button>
                  </div>
                ))}
                <div className="edit-block-menu">
                  <button onClick={() => addBlock('text')}>+ Add Text</button>
                  <button onClick={() => addBlock('todo')}>+ Add Todo</button>
                  <button>Save / Update</button>
                </div>
              </>
            ) : (
              <div className="home-page">
                <h1>Welcome to LevelNotes!</h1>
                <img src={darkMode ? dark : light} alt="theme" />
                <p>Select a page or create a new one to start taking notes.</p>
                <h2>Coming Updates...</h2>
                <ul>
                  <li>Chatbot / Summarizer</li>
                </ul>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default App;