import { useState } from 'react'
import { ChevronRight, ChevronDown, File, Folder } from 'lucide-react'

export default function FileTree({ title, icon: Icon, expanded, onToggle, items = [] }) {
  const [expandedFolders, setExpandedFolders] = useState({})

  const toggleFolder = (path) => {
    setExpandedFolders(prev => ({ ...prev, [path]: !prev[path] }))
  }

  const handleFileClick = (item) => {
    if (item.type === 'file') {
      // TODO: Load and display file content in main view
      console.log('Open file:', item.name)
    }
  }

  const renderItem = (item, depth = 0, parentPath = '') => {
    const itemPath = `${parentPath}/${item.name}`
    const isExpanded = expandedFolders[itemPath]

    if (item.type === 'folder') {
      return (
        <div key={itemPath} className="tree-folder">
          <div 
            className="tree-item folder"
            style={{ paddingLeft: `${depth * 16 + 8}px` }}
            onClick={() => toggleFolder(itemPath)}
          >
            {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            <Folder size={14} />
            <span>{item.name}</span>
          </div>
          {isExpanded && item.children && (
            <div className="tree-children">
              {item.children.map(child => renderItem(child, depth + 1, itemPath))}
            </div>
          )}
        </div>
      )
    }

    return (
      <div 
        key={itemPath}
        className="tree-item file"
        style={{ paddingLeft: `${depth * 16 + 24}px` }}
        onClick={() => handleFileClick(item)}
      >
        <File size={14} />
        <span>{item.name}</span>
      </div>
    )
  }

  return (
    <div className="file-tree">
      <div className="tree-header" onClick={onToggle}>
        {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        {Icon && <Icon size={16} />}
        <span className="tree-title">{title}</span>
        <span className="tree-count">({items.length})</span>
      </div>
      {expanded && (
        <div className="tree-content">
          {items.map(item => renderItem(item))}
        </div>
      )}
    </div>
  )
}

