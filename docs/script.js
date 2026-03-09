// ISBN Scanner - Browser-based ISBN Scanner using html5-qrcode

const books = [];
let html5QrCode = null;
let isScanning = false;

// DOM Elements
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const cameraSelect = document.getElementById('cameraSelect');
const booksList = document.getElementById('booksList');
const countEl = document.getElementById('count');
const saveBtn = document.getElementById('saveBtn');
const downloadBtn = document.getElementById('downloadBtn');
const clearBtn = document.getElementById('clearBtn');
const loadingEl = document.getElementById('loading');

// Initialize camera list
async function initCameras() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(d => d.kind === 'videoinput');
        
        cameraSelect.innerHTML = '<option value="">カメラを選択</option>';
        
        videoDevices.forEach((device, index) => {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.textContent = device.label || `カメラ ${index + 1}`;
            cameraSelect.appendChild(option);
        });
        
        if (videoDevices.length === 0) {
            showToast('カメラが見つかりません', 'error');
        }
    } catch (err) {
        console.error('カメラ一覧取得エラー:', err);
        showToast('カメラへのアクセスが拒否されました', 'error');
    }
}

// Start scanning
async function startScanner() {
    const cameraId = cameraSelect.value;
    if (!cameraId) {
        showToast('カメラを選択してください', 'error');
        return;
    }

    html5QrCode = new Html5Qrcode('reader');
    
    try {
        await html5QrCode.start(
            cameraId,
            {
                fps: 10,
                qrbox: { width: 300, height: 150 },
                aspectRatio: 1.777
            },
            onScanSuccess,
            onScanFailure
        );
        
        isScanning = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;
        cameraSelect.disabled = true;
        showToast('スキャン開始！', 'success');
    } catch (err) {
        console.error('スキャン開始エラー:', err);
        showToast('カメラの起動に失敗しました', 'error');
    }
}

// Stop scanning
async function stopScanner() {
    if (html5QrCode && isScanning) {
        try {
            await html5QrCode.stop();
            isScanning = false;
            startBtn.disabled = false;
            stopBtn.disabled = true;
            cameraSelect.disabled = false;
            showToast('スキャン停止', 'success');
        } catch (err) {
            console.error('スキャン停止エラー:', err);
        }
    }
}

// ISBN normalization (convert EAN-13 to ISBN-13)
function normalizeISBN(code) {
    const digits = code.replace(/[^0-9Xx]/g, '');
    
    // Already ISBN-13
    if (digits.length === 13) {
        return digits;
    }
    
    // Convert ISBN-10 to ISBN-13
    if (digits.length === 10) {
        const core = '978' + digits.slice(0, 9);
        let total = 0;
        
        for (let i = 0; i < 12; i++) {
            const n = parseInt(core[i]);
            total += i % 2 === 0 ? n : n * 3;
        }
        
        const checkDigit = (10 - (total % 10)) % 10;
        return core + checkDigit;
    }
    
    return null;
}

// Scan success callback
async function onScanSuccess(decodedText) {
    const isbn = normalizeISBN(decodedText);
    
    if (!isbn) {
        console.log('ISBNとして認識できませんでした:', decodedText);
        return;
    }
    
    // Check if already scanned
    if (books.some(b => b.isbn === isbn)) {
        showToast('既に登録されています', 'error');
        return;
    }
    
    // Add book
    const book = {
        isbn: isbn,
        title: '取得中...',
        author: '',
        cover: null,
        loading: true
    };
    
    books.unshift(book);
    updateBooksList();
    updateButtons();
    
    // Fetch book info from Google Books API
    await fetchBookInfo(isbn, book);
}

// Scan failure callback
function onScanFailure(error) {
    // Silently ignore scan failures (too many false positives)
}

// Fetch book info from Google Books API
async function fetchBookInfo(isbn, book) {
    try {
        const response = await fetch(
            `https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}`
        );
        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
            const info = data.items[0].volumeInfo;
            book.title = info.title || 'タイトル不明';
            book.author = info.authors ? info.authors.join(', ') : '著者不明';
            book.cover = info.imageLinks ? info.imageLinks.thumbnail : null;
        } else {
            book.title = '書籍情報が見つかりません';
            book.author = '-';
        }
    } catch (err) {
        console.error('APIエラー:', err);
        book.title = '取得失敗';
        book.author = '-';
    }
    
    book.loading = false;
    updateBooksList();
}

// Update books list UI
function updateBooksList() {
    if (books.length === 0) {
        booksList.innerHTML = '<p class="empty-message">まだ本がスキャンされていません</p>';
        countEl.textContent = '0冊';
        return;
    }
    
    countEl.textContent = `${books.length}冊`;
    
    booksList.innerHTML = books.map(book => {
        if (book.loading) {
            return `
                <div class="book-card" data-isbn="${book.isbn}">
                    <div class="book-cover">本</div>
                    <div class="book-info">
                        <div class="book-title">${book.isbn}</div>
                        <div class="book-loading">情報を取得中...</div>
                        <div class="book-isbn">ISBN: ${book.isbn}</div>
                    </div>
                </div>
            `;
        }
        
        const coverHtml = book.cover 
            ? `<img class="book-cover" src="${book.cover}" alt="表紙" onerror="this.outerHTML='<div class=\\'book-cover\\'>本</div>'">`
            : '<div class="book-cover">本</div>';
        
        return `
            <div class="book-card" data-isbn="${book.isbn}">
                ${coverHtml}
                <div class="book-info">
                    <div class="book-title">${escapeHtml(book.title)}</div>
                    <div class="book-author">${escapeHtml(book.author)}</div>
                    <div class="book-isbn">ISBN: ${book.isbn}</div>
                </div>
            </div>
        `;
    }).join('');
}

// Update button states
function updateButtons() {
    const hasBooks = books.length > 0;
    saveBtn.disabled = !hasBooks;
    downloadBtn.disabled = !hasBooks;
    clearBtn.disabled = !hasBooks;
}

// Save to CSV
function saveToCSV() {
    const csvContent = generateCSV();
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    const timestamp = new Date().toISOString().slice(0, 10);
    const filename = `scanned_books_${timestamp}.csv`;
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    
    URL.revokeObjectURL(url);
    showToast(`保存しました: ${filename}`, 'success');
}

// Download CSV (same as save for browser)
function downloadCSV() {
    saveToCSV();
}

// Clear all books
function clearBooks() {
    if (confirm('スキャン結果をクリアしますか？')) {
        books.length = 0;
        updateBooksList();
        updateButtons();
        showToast('クリアしました', 'success');
    }
}

// Generate CSV content
function generateCSV() {
    const headers = ['ISBN', 'タイトル', '著者'];
    const rows = books.map(book => [
        book.isbn,
        book.title,
        book.author
    ]);
    
    return [headers, ...rows]
        .map(row => row.map(cell => `"${cell}"`).join(','))
        .join('\n');
}

// Show toast notification
function showToast(message, type = 'info') {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.remove(), 3000);
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Event listeners
startBtn.addEventListener('click', startScanner);
stopBtn.addEventListener('click', stopScanner);
saveBtn.addEventListener('click', saveToCSV);
downloadBtn.addEventListener('click', downloadCSV);
clearBtn.addEventListener('click', clearBooks);

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initCameras();
});

// Re-init cameras when permissions change
navigator.mediaDevices.addEventListener('devicechange', initCameras);
