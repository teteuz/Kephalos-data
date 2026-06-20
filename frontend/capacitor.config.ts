import type { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'com.kephalosdata.app',
  appName: 'Kephalos Data',
  webDir: 'dist',
  server: {
    // Em desenvolvimento, aponte para o IP local do seu computador
    // para o app do celular conseguir se conectar ao backend.
    // Comente estas duas linhas para build de produção.
    // url: 'http://192.168.1.157:3000',
    // cleartext: true,
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 1500,
      backgroundColor: '#080808',
      showSpinner: false,
    },
  },
}

export default config
