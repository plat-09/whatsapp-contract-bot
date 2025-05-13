const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys')
const { Boom } = require('@hapi/boom')
const axios = require('axios')

async function startWhatsAppBot() {
  const { state, saveCreds } = await useMultiFileAuthState('auth_info')

  const sock = makeWASocket({
    auth: state,
    printQRInTerminal: true
  })

  sock.ev.on('creds.update', saveCreds)

  sock.ev.on('connection.update', ({ connection, lastDisconnect }) => {
    if (connection === 'close') {
      const shouldReconnect = lastDisconnect.error?.output?.statusCode !== DisconnectReason.loggedOut
      console.log('Соединение закрыто. Переподключение:', shouldReconnect)
      if (shouldReconnect) {
        startWhatsAppBot()
      }
    } else if (connection === 'open') {
      console.log('✅ WhatsApp-бот подключен')
    }
  })

  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type !== 'notify') return

    const msg = messages[0]
    if (!msg.message || msg.key.fromMe) return

    const sender = msg.key.remoteJid
    const text = msg.message?.conversation || msg.message?.extendedTextMessage?.text || ''

    console.log(`💬 Новое сообщение от ${sender}: ${text}`)

    // Пробуем запросить информацию по договору у Telegram-сервера
    try {
      const response = await axios.post('http://localhost:5005/get-contract', {
        number: text.trim()
      })

      const { text: replyText, file } = response.data

      // Сначала отправим текст
      await sock.sendMessage(sender, { text: replyText })

      // Потом отправим PDF-файл
      await sock.sendMessage(sender, {
        document: { url: file },
        mimetype: 'application/pdf',
        fileName: 'Договор.pdf'
      })

    } catch (error) {
      const errMsg = error.response?.data?.text || "❌ Произошла ошибка при обработке номера договора"
      await sock.sendMessage(sender, { text: errMsg })
    }
  })
}

startWhatsAppBot()