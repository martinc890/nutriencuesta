import { test, expect } from '@playwright/test';

test('test ejemplo encuesta', async ({ page }) => {
  await page.goto('https://prueba-form-rho.vercel.app/');
  const urlFinal = 'https://prueba-form-rho.vercel.app/finalEncuesta.html';

    // Rellenar el campo de entrada 'birthYear' con el número 20
await page.locator('input#birthYear').fill('20');

  // Seleccionar la opción 'Hombre' del menú desplegable 'gender'
  await page.locator('select#selectGender').selectOption('hombre');

  // Clickear opciones de encuesta
  await page.locator('input#tex4').click();
  await page.locator('input#con1').click();
  await page.locator('input#sab3').click();

   // Rellenar el campo de entrada con "Muy bueno!"
   await page.locator('input#respuesta7').fill('Muy bueno!');

  //Click en enviar 
  await page.locator('button.finish-button').click();

  //Espera que la pagina te lleve a la url final, una vez entregada la encuesta completa
  await expect(page.url()).toBe(urlFinal);
})
  

test('verificar que no se entrega si no esta completo', async ({ page }) => {
    await page.goto('https://prueba-form-rho.vercel.app/');
    const urlInicial = 'https://prueba-form-rho.vercel.app/';

      // Rellenar el campo de entrada 'birthYear' con el número 20
  await page.locator('input#birthYear').fill('20');

    // Seleccionar la opción 'Hombre' del menú desplegable 'gender'
    await page.locator('select#selectGender').selectOption('hombre');

    // Clickear opciones de encuesta
    await page.locator('input#tex4').click();
    await page.locator('input#con1').click();
    await page.locator('input#sab3').click();

    //Click en enviar 

    await page.locator('button.finish-button').click();

    //Espera que la pagina siga en la misma url, osea que no se entrego y te mando a la siguiente
    await expect(page.url()).toBe(urlInicial);
})
    