
// npm run dev


// Push frontend changes
// cd frontend
// npm run build
// cd ..
// git add frontend
// git commit -m "rebuilt frontend"
// git push origin main
// git subtree push --prefix frontend/dist origin gh-pages


<script>

import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Message from 'primevue/message';
import Select from 'primevue/select';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import SelectButton from 'primevue/selectbutton';
import InputNumber from 'primevue/inputnumber';
import ToggleSwitch from 'primevue/toggleswitch';

// https://www.npmjs.com/package/vue-toast-notification
import {useToast} from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';

import axios from 'axios';


const $toast = useToast();


export default {


  components: {
    InputText,
    Button,
    Message,
    Select,
    DataTable,
    Column,
    SelectButton,
    InputNumber,
    ToggleSwitch,
  },

  data() {
    return {

      addr: 'http://127.0.0.1' + ':' + '8000',
      // addr: 'http://34.82.55.106' + ':' + '8000',
      // addr: 'https://market-sim.duckdns.org',
      // addr: 'https://market-sim.serverpit.com',

      data_getSellOrders: null,
      data_getPrice: null,
      data_getAssets: null,
      data_getPeople: null,
      data_getResources: null,

      data_createPerson: null,
      data_sell: null,
      data_buy: null,
      data_cancelSell: null,

      error: null,

      selectedPerson: '',
      createdPerson: '',
      currentPerson: '',

      money: null,
      selectedResource: null,
      sellQuantity: null,
      sellPrice: null,

      currentPersonSales: null,
      selectedSaleForCancel: null,

      currentResource: null,
      selectedSale: null,
      data_getSellOrdersForBuying: null,

      buyQuantity: null,
      numAvailable: null,
      pricePerUnit: null,
      firstPrice: null,

      adminToggle: null,
      adminMoney: null,
      adminDepositWithdraw: null,

      adminDepositWithdrawResponse: null,

      adminSelectMoneyOrResorce: null,
      adminSelectedResource: null,
      adminResourceAmount: null,
      adminDepositWithdrawResource: null,
      adminGiveOrTakeResourceResponse: null,

      newResourceData: null,
      selectButtonResource: null,

      newResourceType: null,

      typingSessionKey: null,
      sessionKey: null,

      data_sessionKey: null,

    };
  },

  mounted() {
    document.title = 'Market Simulator'; // set site title
  },

  methods: {

    makeToast(message, b_success=true) {

      var success_str;

      if (b_success) {
        success_str = 'success';
      }
      else {
        success_str = 'error';
      }

      this.$toast.open({
        message: message,
        type: success_str, // success, info, warning, error, default
        position: 'bottom-right',
        duration: 3000,
      });
    },

    async getSellOrders(resource_type, name=null, b_quantity_available=false) {
      try {

        let url = this.addr + '/get_sell_orders'

        const headers = { 'Content-Type': 'application/json' };
        var params = {};

        params = {  'session_key': this.sessionKey,
                      'resource_type': resource_type
                  };

        if (name !== null) {
          params['name'] = name;
        }

        if (b_quantity_available) {
          params['b_quantity_available'] = true;
        }

        const response = await axios({
          method: 'get',
          url: url,
          headers: headers,
          params: params,
        });

        console.log(response.data);

        this.data_getSellOrders = response.data;
        this.error = null;
      } catch (err) {
        this.data_getSellOrders = null;
        this.error = err.message;
      }

    },

    async getPrice(resource_type, quantity) {
      try {

        let url = this.addr + '/get_price'

        const headers = { 'Content-Type': 'application/json' };
        const params = { 'session_key': this.sessionKey,
                         'resource_type': resource_type,
                         'quantity': quantity };

        const response = await axios({
          method: 'get',
          url: url,
          headers: headers,
          params: params,
        });

        console.log(response.data);

        this.data_getPrice = response.data;
        this.error = null;

        this.pricePerUnit = this.data_getPrice.data.price / quantity;
        this.pricePerUnit = this.pricePerUnit.toFixed(2);

      } catch (err) {
        this.data_getPrice = null;
        this.error = err.message;
      }
    },

    async getAssets(name) {
      try {

        let url = this.addr + '/get_assets'

        const headers = { 'Content-Type': 'application/json' };
        const params = {  'session_key': this.sessionKey,
                          'name': String(name) 
                        };

        const response = await axios({
          method: 'get',
          url: url,
          headers: headers,
          params: params,
        });

        console.log(response.data);

        this.data_getAssets = response.data;
        this.error = null;

        this.money = this.data_getAssets.data.cash;

      } catch (err) {
        this.data_getAssets = null;
        this.error = err.message;
      }

    },

    async getPeople() {
      try {

        let url = this.addr + '/get_people'

        const headers = { 'Content-Type': 'application/json' };
        const params = {  'session_key': this.sessionKey,
                        };

        const response = await axios({
          method: 'get',
          url: url,
          headers: headers,
          params: params,
        });

        console.log(response.data);

        this.data_getPeople = response.data;
        this.error = null;
      } catch (err) {
        this.data_getPeople = null;
        this.error = err.message;
      }
    },


    async getResources() {
      try {

        let url = this.addr + '/get_resources'

        const headers = { 'Content-Type': 'application/json' };
        const params = {  'session_key': this.sessionKey,
                        };

        const response = await axios({
          method: 'get',
          url: url,
          headers: headers,
          params: params,
        });

        console.log(response.data);

        this.data_getResources = response.data;
        this.error = null;
      } catch (err) {
        this.data_getResources = null;
        this.error = err.message;
      }
    },


    async createPerson(name) {

      if (name == '') {

        this.makeToast('Missing info', false);

        return;
      }

      let response;

      try {

        let url = this.addr + '/create_person'

        const headers = { 'Content-Type': 'application/json' };

        const body = { 'session_key': this.sessionKey,
                       'name': String(name),
                       'cash': 0,
                       'resource_dict': {} };
                       // 'resource_dict': {'apple': 4} };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_createPerson = response.data;
        this.error = null;
      } catch (err) {
        this.data_createPerson = null;
        this.error = err.message;
      }

      // set currentPerson
      this.setCurrentPerson(name);

      // Update
      this.getPeople();

      this.makeToast(response.data.message, response.data.b_success);

    },

    async sell_order(name, resource_type, quantity, price) {

      if (name === null || resource_type === null || quantity === null || price === null) {

        this.makeToast('Missing info', false);

        return;
      };

      let response;

      try {

        let url = this.addr + '/sell_order'

        const headers = { 'Content-Type': 'application/json' };

        const body = { 'session_key': this.sessionKey,
                       'name': name,
                       'resource_type': resource_type,
                       'quantity': quantity,
                       'price': price };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        // get updated list of resources
        await this.getAssets(name);

        // get updated sell orders
        await this.getSellOrdersForPerson(resource_type)


        // reset fields
        this.sellQuantity = null;
        this.sellPrice = null;

        this.data_sell = response.data;
        this.error = null;


        await this.getSellOrdersForBuying(this.currentResource);

      } catch (err) {
        this.data_sell = null;
        this.error = err.message;
      }

      this.makeToast(response.data.message, response.data.b_success);

    },

    async buy_now(name, resource_type, quantity) {

      let response;

      try {

        let url = this.addr + '/buy_now'

        const headers = { 'Content-Type': 'application/json' };

        const body = { 'session_key': this.sessionKey,
                       'name': name,
                       'resource_type': resource_type,
                       'quantity': quantity };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_buy = response.data;
        this.error = null;
      } catch (err) {
        this.data_buy = null;
        this.error = err.message;
      }

      // refresh assets
      if (this.currentPerson) {
        await this.getAssets(this.currentPerson);
      }

      // reset
      this.buyQuantity = null;

      // update sell orders for buying
      await this.getSellOrdersForBuying(resource_type);

      this.makeToast(response.data.message, response.data.b_success);

    },


    async sell_now(name, resource_type, quantity) {

      let response;

      try {

        let url = this.addr + '/sell_now'

        const headers = { 'Content-Type': 'application/json' };

        const body = { 'session_key': this.sessionKey,
                       'name': name,
                       'resource_type': resource_type,
                       'quantity': quantity };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_buy = response.data;
        this.error = null;
      } catch (err) {
        this.data_buy = null;
        this.error = err.message;
      }

      // refresh assets
      if (this.currentPerson) {
        await this.getAssets(this.currentPerson);
      }

      // reset
      this.sellNowQuantity = null;

      // update sell orders for buying
      await this.getSellOrdersForBuying(resource_type);

      this.makeToast(response.data.message, response.data.b_success);

    },


    async sell_now_or_sell_order() {

      if (this.currentPerson === null || this.currentResource === null || this.sellQuantity === null) {

        this.makeToast('Missing info', false);

        return;
      }

      if (this.sellPrice != null) {
        await this.sell_order(this.currentPerson, this.currentResource, this.sellQuantity, this.sellPrice);
      }
      else {
        await this.sell_now(this.currentPerson, this.currentResource, this.sellQuantity);
      }

    },


    async cancelSellOrder(sell_id) {
      try {

        let url = this.addr + '/cancel_sell_order'

        const headers = { 'Content-Type': 'application/json' };

        const body = {  'session_key': this.sessionKey,
                        'sell_id': sell_id 
                      };

        const response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_cancelSell = response.data;
        this.error = null;
      } catch (err) {
        this.data_cancelSell = null;
        this.error = err.message;
      }

      // refresh assets
      await this.getAssets(this.currentPerson);

      // refresh sell orders
      await this.getSellOrdersForPerson(this.currentResource);

      // update buy market
      await this.getSellOrdersForBuying(this.currentResource);

    },


    async getSellOrdersForPerson(resource_type) {

      // Set resource type
      this.currentResource = resource_type;

      await this.getSellOrders(resource_type, this.currentPerson);

      if (this.currentPerson) {
        this.currentPersonSales = this.data_getSellOrders.data.sell_list;
      }
      else {
        this.currentPersonSales = null;
      }

      // reset
      this.selectedSaleForCancel = null;
    },


    async setCurrentPerson(name) {
      this.currentPerson = name;
      this.selectedPerson = name;

      await this.getAssets(name);

      if (this.currentResource !== null) {
        // get updated sell orders
        await this.getSellOrdersForPerson(this.currentResource)
      }

      // reset
      this.selectedResource = null;
      this.currentPersonSales = null;

    },

    async setCurrentResource(resource_type) {
      this.currentResource = resource_type;

      if (this.currentPerson !== null) {
        // get updated sell orders
        await this.getSellOrdersForPerson(resource_type)
      }

      // reset
      if (this.selectedResource !== null) {
        if (this.selectedResource.type != resource_type) {
          this.selectedResource = null;
        }
      }

    },



    async getSellOrdersForBuying(resource_type) {

      await this.getSellOrders(resource_type, null, true);

      this.data_getSellOrdersForBuying = this.data_getSellOrders;

      // Add up all the quantities to get total number for sale
      var num_available = 0;
      for (let i = 0; i < this.data_getSellOrdersForBuying.data.sell_list.length; i++) {
        num_available += this.data_getSellOrdersForBuying.data.sell_list[i].quantity_available;
      }

      // Get first price
      if (this.data_getSellOrdersForBuying.data.sell_list.length > 0) {
        this.firstPrice = this.data_getSellOrdersForBuying.data.sell_list[0].price;
      }
      else {
        this.firstPrice = null;
      }

      this.numAvailable = num_available;

      // reset
      this.buyQuantity = null;

    },


    async depositOrWithdraw() {

      if (this.currentPerson === null || this.adminMoney === null || this.adminDepositWithdraw === null) {

        // toast
        this.makeToast('Missing info', false);

        return;
      }

      let response;

      try {

        var b_deposit = false;
        if (this.adminDepositWithdraw == 'Deposit') {
          // add money
          b_deposit = true;
        }
        else {
          // subract money
          b_deposit = false;
        }

        let url = this.addr + '/deposit_or_withdraw'

        const headers = { 'Content-Type': 'application/json' };
        const body = { 'session_key': this.sessionKey,
                       'name': this.currentPerson,
                       'b_deposit': b_deposit,
                       'dollars': this.adminMoney
                      };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.adminDepositWithdrawResponse = response.data;
        this.error = null;
      } catch (err) {
        this.adminDepositWithdrawResponse = null;
        this.error = err.message;
      }

      // update money
      await this.getAssets(this.currentPerson);

      this.makeToast(response.data.message, response.data.b_success);

    },


    async giveOrTakeResource() {

      if (this.currentResource === null || this.currentPerson === null || this.adminResourceAmount === null || this.adminDepositWithdrawResource === null)  {

        this.makeToast('Missing info', false);

        return;
      }

      let response;

      try {

        var b_deposit = false;
        if (this.adminDepositWithdrawResource == 'Deposit') {
          // add money
          b_deposit = true;
        }
        else {
          // subract money
          b_deposit = false;
        }

        let url = this.addr + '/give_or_take_resource'

        const headers = { 'Content-Type': 'application/json' };

        const body = { 'session_key': this.sessionKey,
                       'name': this.currentPerson,
                       'resource_type': this.currentResource,
                       'b_deposit': b_deposit,
                       'quantity': this.adminResourceAmount
                      };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.adminGiveOrTakeResourceResponse = response.data;
        this.error = null;
      } catch (err) {
        this.adminGiveOrTakeResourceResponse = null;
        this.error = err.message;
      }

      // update person's resources
      this.getAssets(this.currentPerson);

      this.makeToast(response.data.message, response.data.b_success);

    },


    async newResource(resource_type) {

      if (resource_type === null) {

        this.makeToast('Missing info', false);

        return;
      }

      let response;

      try {

        let url = this.addr + '/new_resource'

        const headers = { 'Content-Type': 'application/json' };

        const body = { 
                       'session_key': this.sessionKey,
                       'resource_type': String(resource_type)
                      };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.newResourceData = response.data;
        this.error = null;
      } catch (err) {
        this.newResourceData = null;
        this.error = err.message;
      }

      // reset
      this.newResourceType = null;

      // update
      await this.getResources();

      this.currentResource = resource_type;

      this.makeToast(response.data.message, response.data.b_success);

    },



    async setSessionKey() {
      this.sessionKey = this.typingSessionKey;
      this.typingSessionKey = null;

      if (this.sessionKey === null) {
        // reset
        this.data_getPeople = null;
        this.currentPerson = null;
        this.money = null;
        this.data_getAssets = null;
        this.currentResource = null;
        this.data_getResources = null;
        this.selectedResource = null;
        this.adminToggle = null;
        this.selectedPerson = '';

        this.makeToast('Missing info', false);

        return;
      }

      let response;

      try {

        let url = this.addr + '/create_session';

        const headers = { 'Content-Type': 'application/json' };

        const body = { 'session_key': this.sessionKey,
                       };

        response = await axios({
          method: 'post',
          url: url,
          headers: headers,
          data: body,
        });

        console.log(response.data);

        this.data_sessionKey = response.data;
        this.error = null;
      } catch (err) {
        this.data_sessionKey = null;
        this.error = err.message;
      }

      // reset
      this.currentPerson = null;
      this.money = null;
      this.data_getAssets = null;
      this.currentResource = null;
      this.data_getResources = null;
      this.selectedResource = null;
      this.adminToggle = null;

      // Get list of resources
      await this.getResources();

      // Get list of people
      await this.getPeople();

      this.makeToast(response.data.message, response.data.b_success);

    },



    async debugFunc() {
      console.log('DEBUG A0')
    },

 


  },

};



</script>





<template>


  <div :style="{ backgroundColor: '#f0f2f5', width: '100vw' }">



    <div class="flexbox-container-top">
      <div class="flexbox-item flexbox-item-4">

        <div style="text-align:center;">
          <p style="display:inline-block;" class="relative text-2xl text-center">
            <i class="pi pi-key" style="font-size: 2.0rem;"></i>
            Session
          </p>
        </div>

        <div v-if="sessionKey">
          <p style="font-weight: bold;" class="relative text-lg text-center text-blue-500">{{ sessionKey }}</p>
        </div>
        <div v-else>
          <p class="relative text-lg text-center">enter a session key</p>
        </div>

        <div style="text-align:center;">
          <InputText type="text" v-model="typingSessionKey" placeholder="session key" size="small" style="text-align:center;" @keyup.enter="setSessionKey" />
        
          <Button size="small" type="submit" severity="info" label="Submit" @click="setSessionKey" />
        </div>

      </div>



      <div class="flexbox-item flexbox-item-6">

        <div style="text-align:center;">
          <p style="display:inline-block;" class="relative text-2xl text-center">
            <i class="pi pi-user" style="font-size: 2.0rem"></i>
            Person
          </p>
        </div>

        <div v-if="currentPerson">
          <p style="font-weight: bold;" class="relative text-lg text-center text-blue-500">{{ currentPerson }}</p>
        </div>
        <div v-else>
          <p class="relative text-lg text-center">select a person</p>
        </div>


        <div v-if="data_getPeople" style="text-align:center;">
          <Select v-model="selectedPerson" :options="data_getPeople.data.people" placeholder="person" size="small" class="w-full md:w-56"  filter @update:modelValue="setCurrentPerson(selectedPerson)"/>
        </div>

      </div>



      <div class="flexbox-item flexbox-item-7">

        <div style="text-align:center;">
          <p style="display:inline-block;" class="relative text-2xl text-center">
            <i class="pi pi-ticket" style="font-size: 2.0rem"></i>
            Resource
          </p>
        </div>


        <div v-if="currentResource">
          <p style="font-weight: bold;" class="relative text-lg text-center text-blue-500">{{ currentResource }}</p>
        </div>
        <div v-else>
          <p class="relative text-lg text-center">select a resource</p>
        </div>


        <div v-if="data_getResources && sessionKey" style="text-align:center;">
          <Select v-model="currentResource" :options="data_getResources.data.resources" placeholder="resource" size="small" class="w-full md:w-56" filter @update:modelValue="setCurrentResource(currentResource)"/>
        </div>


      </div>



    </div>







    <div class="flexbox-container">
      <div class="flexbox-item flexbox-item-1">

        <div style="text-align:center;">
          <p style="display:inline-block;" class="relative text-2xl text-center">
            <i class="pi pi-building-columns" style="font-size: 2.0rem"></i>
            Admin
          </p>
        </div>
        <br>


        <div v-if="sessionKey" >
          <div style="text-align:center;">
            <p style="display:inline-block;" class="relative text-lg text-center">
              create a new person
            </p>
          </div>

          <div style="text-align:center;">
            <InputText type="text" v-model="createdPerson" placeholder="name" size="small" style="text-align:center;" />

              <Button size="small" type="submit" severity="info" label="Submit" @click="createPerson(createdPerson)" />
          </div>
        </div>

        <br>





        <div v-if="sessionKey" >
          <div style="text-align:center;">
            <p style="display:inline-block;" class="relative text-lg text-center">
              create a new resource
            </p>
          </div>

          <div style="text-align:center;">
            <InputText type="text" v-model="newResourceType" placeholder="resource" size="small" style="text-align:center;" />

            <Button size="small" type="submit" severity="info" label="Submit" @click="newResource(newResourceType)" />
          </div>
        </div>


        <br>


        <div v-if="currentPerson">

          <div style="text-align:center;">
            <p style="display:inline-block;" class="relative text-lg text-center">
              deposit or withdraw money
            </p>
          </div>


          <div style="text-align:center;">
            <SelectButton v-model="adminDepositWithdraw" :options="['Deposit', 'Withdraw']" size="small" />
          </div>

          <div style="text-align:center;">
            <InputNumber v-model="adminMoney" placeholder="amount" inputId="currency-us" mode="currency" currency="USD" locale="en-US" size="small" style="text-align:center;" />

            <Button size="small" type="submit" severity="info" label="Submit" @click="depositOrWithdraw" />
          </div>

        </div>



          <br>


        <div v-if="currentPerson && currentResource">


          <div style="text-align:center;">
            <p style="display:inline-block;" class="relative text-lg text-center">
              deposit or withdraw resource
            </p>
          </div>

          <div style="text-align:center;">
            <SelectButton v-model="adminDepositWithdrawResource" :options="['Deposit', 'Withdraw']" size="small" />
          </div>

          <div style="text-align:center;">
            <InputNumber v-model="adminResourceAmount" placeholder="quantity" inputId="integeronly" size="small" style="text-align:center;" />

            <Button size="small" type="submit" severity="info" label="Submit" @click="giveOrTakeResource" />
          </div>

        </div>

      </div>







      <div class="flexbox-item flexbox-item-2">

        <div style="text-align:center;">
          <p style="display:inline-block;" class="relative text-2xl text-center">
            <i class="pi pi-shop" style="font-size: 2.0rem"></i>
            Sell
          </p>
        </div>

        <br>


        <div v-if="data_getAssets">


          <DataTable selectionMode="single" v-model:selection="selectedResource" :value="data_getAssets.data.resource_list" size="small" scrollable scrollHeight="204px" tableStyle="min-width: 10rem" @row-select="setCurrentResource(selectedResource.type)" >
            <Column field="type" header="Resource"></Column>
            <Column field="quantity" header="Quantity"></Column>
          </DataTable>

        </div>

        <br>


        <div v-if="currentPerson && currentResource">



          <div style="text-align:center;">

            <InputNumber v-model="sellQuantity" inputId="integeronly" placeholder="quantity" :model-value="sellQuantity" @input="(e) => (sellQuantity = e.value)" size="small" style="text-align:center;" />

            <InputNumber v-model="sellPrice" inputId="price_input" mode="currency" currency="USD" placeholder="price (optional)" :model-value="sellPrice" @input="(e) => (sellPrice = e.value)" size="small" style="text-align:center;" />


              <Button size="small" type="submit" severity="info" label="Submit" @click="sell_now_or_sell_order()" />
          </div>


          <br>


          <p class="relative text-lg text-center">your sell orders</p>

          <DataTable selectionMode="single" v-model:selection="selectedSaleForCancel" :value="currentPersonSales" size="small" scrollable scrollHeight="164px" tableStyle="min-width: 10rem" >
            <Column field="quantity" header="Quantity"></Column>
            <Column field="price" header="Price"></Column>
          </DataTable>

          <div v-if="selectedSaleForCancel" >
            <Button style="width: 100%;" type="submit" severity="info" label="cancel listing" size="small" @click="cancelSellOrder(selectedSaleForCancel.id)" rounded />
          </div>


        </div>

      </div>









      <div class="flexbox-item flexbox-item-3">

        <div style="text-align:center;">
          <p style="display:inline-block;" class="relative text-2xl text-center">
            <i class="pi pi-shopping-bag" style="font-size: 2.0rem"></i>
            Buy
          </p>
        </div>
        <br>

        <div v-if="money != null">
          <span style="font-weight: bold;" class="p-2 relative text-lg" >Money: &nbsp; ${{money.toFixed(2)}}</span>
        </div>


        <div v-if="data_getResources && sessionKey">
          <div v-if="currentResource">
            <p style="font-weight: bold;" class="relative text-lg text-center">Resource: {{ currentResource }}</p>
          </div>
          <div v-else>
            <p class="relative text-lg text-center">Select a resource</p>
          </div>
        </div>


        <div v-if="data_getResources && sessionKey">
          <Select v-model="currentResource" :options="data_getResources.data.resources" placeholder="Select resource" class="w-full md:w-56" filter @update:modelValue="getSellOrdersForBuying(currentResource)"/>
        </div>

        <div v-if="currentResource && data_getSellOrdersForBuying">

          <div v-if="firstPrice">
            <p class="relative text-lg text-center">Available: {{numAvailable}} &nbsp; &nbsp; &nbsp; Price: ${{firstPrice.toFixed(2)}}</p>
          </div>
          <div v-else>
            <p class="relative text-lg text-center">Available: {{numAvailable}}</p>
          </div>

          <div v-if="currentPerson">

            <InputNumber v-model="buyQuantity" inputId="integeronly" placeholder="Buy quantity" fluid @update:modelValue="getPrice(currentResource, buyQuantity)" />

            <div v-if="buyQuantity && data_getPrice && data_getPrice.data.price">
              <span class="p-2 relative text-lg" >Total Price: &nbsp; ${{data_getPrice.data.price.toFixed(2)}} &nbsp; &nbsp; Unit Price &nbsp; ${{pricePerUnit}}</span>

              <div v-if="(money != null) && (money >= data_getPrice.data.price)">
                <Button style="width: 100%;" type="submit" severity="info" label="Submit" @click="buy_now(currentPerson, currentResource, buyQuantity)" rounded />
              </div>

            </div>

          </div>


        </div>

      </div>



    </div>


  </div>

  
</template>



<style scoped>


.flexbox-container-top {
  display: flex;
  justify-content: space-around;
  height: 16vh;
  min-height: 130px;
}

.flexbox-container-bottom {
  display: flex;
  justify-content: space-around;
  height: 65vh;
}

.flexbox-container {
  display: flex;
  justify-content: space-around;
  height: 84vh;
}

.flexbox-item {
  width: 300px;
  margin: 8px;
  border: 3px solid #b4bed4;
  background-color: #ffffff;
}

.flexbox-item-1 {
  flex-grow: 1;
}

.flexbox-item-2 {
  flex-grow: 1;
}

.flexbox-item-3 {
  flex-grow: 1;
}

.flexbox-item-4 {
  flex-grow: 1;
}

.flexbox-item-5 {
  flex-grow: 1;
}

.flexbox-item-6 {
  flex-grow: 1;
}

.flexbox-item-7 {
  flex-grow: 1;
}




</style>
