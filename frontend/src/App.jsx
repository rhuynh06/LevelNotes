import { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [pages, setPages] = useState([]);
  const [selectedPage, setSelectedPage] = useState(null);
  const [blocks, setBlocks] = useState([]);
  const [newPageTitle, setNewPageTitle] = useState('');
  const [darkMode, setDarkMode] = useState(false);
  const [undoStack, setUndoStack] = useState([]);
  const [redoStack, setRedoStack] = useState([]);

  const site = 'http://127.0.0.1:5000';

  useEffect(() => {
    fetch(`${site}/pages`)
      .then(res => res.json())
      .then(pages => {
        setPages(pages);
        if (pages.length > 0) {
          selectPage(pages[0]);  // Automatically load first page and blocks
        }
      });
  }, []);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.setAttribute('data-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
  }, [darkMode]);

  const selectPage = (page) => {
    setSelectedPage(page);
    fetch(`${site}/pages/${page.id}/blocks`)
      .then(res => res.json())
      .then(setBlocks);
  };

  const createPage = () => {
    fetch(`${site}/pages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: newPageTitle }),
    })
      .then(res => res.json())
      .then(page => {
        setPages([...pages, page]);
        setNewPageTitle('');
      });
  };

  const renamePage = (pageId, newTitle) => {
    pushToUndoStack();

    fetch(`${site}/pages/${pageId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: newTitle }),
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
    fetch(`${site}/pages/${pageId}`, { method: 'DELETE' }).then(() => {
      setPages(pages.filter(p => p.id !== pageId));
      if (selectedPage?.id === pageId) {
        setSelectedPage(null);
        setBlocks([]);
      }
    });
  };

  const addBlock = (type = 'text') => {
    if (!selectedPage) return; // avoid errors if no page selected
    fetch(`${site}/blocks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        page_id: selectedPage.id,
        type: type,
        content: type === 'todo' ? { checked: false, text: '' } : '',
        order_index: blocks.length,
      }),
    })
      .then(res => res.json())
      .then((block) => setBlocks([...blocks, block]));
  };

  const updateBlock = (blockId, content) => {
    pushToUndoStack();

    fetch(`${site}/blocks/${blockId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    })
      .then(res => res.json())
      .then((updated) => {
        setBlocks(blocks.map((b) => (b.id === blockId ? updated : b)));
      });
  };

  const deleteBlock = (blockId) => {
    fetch(`${site}/blocks/${blockId}`, { method: 'DELETE' }).then(() => {
      setBlocks(blocks.filter((b) => b.id !== blockId));
    });
  };

  const autoGrow = (el) => {
    if (!el) return;
    el.style.height = 'auto';
    const newHeight = el.scrollHeight + 'px';
    if (el.style.height !== newHeight) {
      el.style.height = newHeight;
    }
  };

  const snapshotState = () => ({
    selectedPage,
    blocks: blocks.map(b => ({ ...b })), // shallow copy
  });

  const pushToUndoStack = () => {
    setUndoStack(prev => {
      const newStack = [...prev, snapshotState()];
      return newStack.length > 20 ? newStack.slice(1) : newStack; // keep max 20
    });
    setRedoStack([]); // clear redo on new action
  };

  const undo = () => {
    if (undoStack.length === 0) return;

    const prevState = undoStack[undoStack.length - 1];
    setUndoStack(undoStack.slice(0, -1));
    
    setRedoStack(prev => [...prev, snapshotState()]);

    setSelectedPage(prevState.selectedPage);
    setBlocks(prevState.blocks);
  };

  const redo = () => {
    if (redoStack.length === 0) return;

    const nextState = redoStack[redoStack.length - 1];
    setRedoStack(redoStack.slice(0, -1));

    setUndoStack(prev => [...prev, snapshotState()]);

    setSelectedPage(nextState.selectedPage);
    setBlocks(nextState.blocks);
  };

  return (
    <div className="app-container">
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
        />
        <button onClick={createPage}>Add Page</button>
        {pages.map((page) => (
          <div
            key={page.id}
            className={`page-item ${selectedPage?.id === page.id ? 'selected' : ''}`}
            onClick={() => selectPage(page)}
          >
            <span>{page.title}</span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                deletePage(page.id);
              }}
            >
              🗑️
            </button>
          </div>
        ))}
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="toggle-mode"
        >
          Toggle {darkMode ? 'Light' : 'Dark'} Mode
        </button>
      </div>

      <div className="editor">
        {selectedPage ? (
          <>
            <textarea
              className="page-title"
              value={selectedPage.title}
              onChange={(e) => {
                renamePage(selectedPage.id, e.target.value);
                autoGrow(e.target);
              }}
              placeholder="Page title"
              style={{ overflow: 'hidden', resize: 'none' }}
            />
            {blocks.map((block) => {
              if (block.type === 'todo') {
                return (
                  <div key={block.id} className="block-row todo-block">
                    <input
                      type="checkbox"
                      checked={block.content.checked}
                      onChange={() => {
                        updateBlock(block.id, {
                          ...block.content,
                          checked: !block.content.checked,
                        });
                      }}
                    />
                    <textarea
                      value={block.content.text}
                      onChange={(e) => {
                        updateBlock(block.id, { ...block.content, text: e.target.value });
                        autoGrow(e.target);
                      }}
                      placeholder="Todo item"
                      style={{ overflow: 'hidden', resize: 'none' }}
                    />
                    <button onClick={() => deleteBlock(block.id)}>🗑️</button>
                  </div>
                );
              } else {
                // Text block
                return (
                  <div key={block.id} className="block-row">
                    <textarea
                      value={block.content}
                      onChange={(e) => {
                        updateBlock(block.id, e.target.value);
                        autoGrow(e.target);
                      }}
                      placeholder="Start typing..."
                      style={{ overflow: 'hidden', resize: 'none' }}
                    />
                    <button onClick={() => deleteBlock(block.id)}>🗑️</button>
                  </div>
                );
              }
            })}
            <div className="add-block-menu">
              <button onClick={() => addBlock('text')}>+ Add Text Block</button>
              <button onClick={() => addBlock('todo')}>+ Add Todo Block</button>
            </div>
            <div className="undo-redo-buttons">
              <button onClick={undo} disabled={undoStack.length === 0}>Undo</button>
              <button onClick={redo} disabled={redoStack.length === 0}>Redo</button>
            </div>
          </>
        ) : (
          <div className="home-page">
            <h1>Welcome to Notes!</h1>
            <p>
              This is the home page. Select a page or create a new one to
              start taking notes.
            </p>
            <h2>Coming Updates...</h2>
            <ul>
              <li>Tags to blocks and pages, for filtering many at once</li>
              <li>Level system for word count + word count + character count</li>
              <li>Chatbot / Summarizer</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
