// Divine Signal UI Logic for Waft
// Handles backend communication and hardware status updates

const WAF_API = "/api/v1";

export default {
  data: {
    cpu_usage: "4%",
    mem_usage: "28MB",
    uptime: "00:12:45",
    logs: []
  },

  onInit() {
    this.startStatusPoller();
    this.addLog("Divine Signal Initialized.");
  },

  startStatusPoller() {
    setInterval(() => {
      // Simulate polling hardware stats
      // In production, this would call fetch() to the local backend
      this.cpu_usage = `${Math.floor(Math.random() * 10) + 2}%`;
      this.mem_usage = `${Math.floor(Math.random() * 5) + 25}MB`;
    }, 2000);
  },

  addLog(msg) {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = `[${timestamp}] ${msg}`;
    this.logs.push(logEntry);
    if (this.logs.length > 5) this.logs.shift();
    this.updateConsole();
  },

  updateConsole() {
    // Logic to update the console text in XML
    const consoleText = this.logs.join('\n');
    this.$element('console_log').setText(consoleText);
  },

  // Toggle handlers
  toggleWiFi() {
    const isActive = this.$element('wifi_status').getText() === "Active";
    if (isActive) {
      this.$element('wifi_status').setText("Inactive");
      this.$element('wifi_status').setStyle('color', '#FF4444');
      this.addLog("WiFi Sniffer Ceased.");
    } else {
      this.$element('wifi_status').setText("Active");
      this.$element('wifi_status').setStyle('color', '#44FF44');
      this.addLog("WiFi Sniffer Engaged.");
    }
  },

  toggleBLE() {
    const isActive = this.$element('ble_status').getText() === "Active";
    if (isActive) {
      this.$element('ble_status').setText("Inactive");
      this.$element('ble_status').setStyle('color', '#FF4444');
      this.addLog("BLE Scanner Ceased.");
    } else {
      this.$element('ble_status').setText("Active");
      this.$element('ble_status').setStyle('color', '#44FF44');
      this.addLog("BLE Scanner Engaged.");
    }
  },

  togglePoisonTap(e) {
    if (e.checked) {
      this.addLog("PoisonTap Intervention Active.");
    } else {
      this.addLog("PoisonTap Intervention Ceased.");
    }
  }
}
