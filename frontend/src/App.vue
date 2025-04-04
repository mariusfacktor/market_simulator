
// npm run dev

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

import axios from 'axios';




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
      data_getMarket: null,
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

      selectPersonButton: null,
      createPersonButton: null,
      selectButtonPerson: null,

      money: null,
      selectedResource: null,
      sellQuantity: null,
      sellPrice: null,

      currentPersonSales: null,
      selectedSaleForCancel: null,

      currentResource: null,
      selectedSale: null,
      data_getMarketForBuying: null,

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

      typingSessionID: null,
      sessionID: null,

    };
  },

  mounted() {
    document.title = 'Market Simulator'; // set site title
    this.getResources();
  },

  methods: {

    async getMarket(resource_type) {
      try {
        const headers = { 'Content-Type': 'application/json' };
        const params = { 'resource_type': resource_type };

        const response = await axios({
          method: 'get',
          url: 'http://127.0.0.1:5000/get_market',
          headers: headers,
          params: params,
        });

        console.log(response.data);

        this.data_getMarket = response.data;
        this.error = null;
      } catch (err) {
        this.data_getMarket = null;
        this.error = err.message;
      }

    },

    async getPrice(resource_type, amount) {
      try {
        const headers = { 'Content-Type': 'application/json' };
        const params = { 'resource_type': resource_type,
                         'amount': amount };

        const response = await axios({
          method: 'get',
          url: 'http://127.0.0.1:5000/get_price',
          headers: headers,
          params: params,
        });

        console.log(response.data);

        this.data_getPrice = response.data;
        this.error = null;

        this.pricePerUnit = this.data_getPrice.data.price / amount;
        this.pricePerUnit = this.pricePerUnit.toFixed(2);

      } catch (err) {
        this.data_getPrice = null;
        this.error = err.message;
      }
    },

    async getAssets(name) {
      try {
        const headers = { 'Content-Type': 'application/json' };
        const params = { 'name': String(name) };

        const response = await axios({
          method: 'get',
          url: 'http://127.0.0.1:5000/get_assets',
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
        const headers = { 'Content-Type': 'application/json' };

        const response = await axios({
          method: 'get',
          url: 'http://127.0.0.1:5000/get_people',
          headers: headers,
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
        const headers = { 'Content-Type': 'application/json' };

        const response = await axios({
          method: 'get',
          url: 'http://127.0.0.1:5000/get_resources',
          headers: headers,
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
      try {
        const headers = { 'Content-Type': 'application/json' };

        const body = { 'name': String(name),
                       'cash': 0,
                       'resource_dict': {} };
                       // 'resource_dict': {'apple': 4} };

        const response = await axios({
          method: 'post',
          url: 'http://127.0.0.1:5000/create_person',
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

    },

    async sell(name, resource_type, amount, price) {
      try {
        const headers = { 'Content-Type': 'application/json' };

        const body = { 'name': name,
                       'resource_type': resource_type,
                       'amount': amount,
                       'price': price };

        const response = await axios({
          method: 'post',
          url: 'http://127.0.0.1:5000/sell',
          headers: headers,
          data: body,
        });

        console.log(response.data);

        // get updated list of resources
        await this.getAssets(name);

        // get updated market
        await this.getMarketForPerson(resource_type)


        // reset fields
        this.sellQuantity = null;
        this.sellPrice = null;

        this.data_sell = response.data;
        this.error = null;
      } catch (err) {
        this.data_sell = null;
        this.error = err.message;
      }
    },

    async buy(name, resource_type, amount) {
      try {
        const headers = { 'Content-Type': 'application/json' };

        const body = { 'name': name,
                       'resource_type': resource_type,
                       'amount': amount };

        const response = await axios({
          method: 'post',
          url: 'http://127.0.0.1:5000/buy',
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

      // update buy market
      await this.getMarketForBuying(resource_type);

    },


    async cancelSell(sell_id) {
      try {
        const headers = { 'Content-Type': 'application/json' };

        const body = { 'sell_id': sell_id };

        const response = await axios({
          method: 'post',
          url: 'http://127.0.0.1:5000/cancel_sell',
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

      // refresh market
      await this.getMarketForPerson(this.selectedResource.resource)

    },


    async buttonSelectOrCreatePerson(name) {

      if (name == 'Select person') {

        this.selectPersonButton = true;
        this.createPersonButton = false;
        this.getPeople()
        }
      else if (name == 'Create person') {

        this.selectPersonButton = false;
        this.createPersonButton = true;
      }
      else {
        this.selectPersonButton = false;
        this.createPersonButton = false;
      }
    },


    async setCurrentPerson(name) {
      this.currentPerson = name;

      await this.getAssets(name);

      // reset
      this.selectedResource = null;
      this.currentPersonSales = null;

    },


    async setSessionID(sessionID) {
      this.sessionID = sessionID;
      this.typingSessionID = null;
    },


    async getMarketForPerson(resource_type) {

      await this.getMarket(resource_type);

      if (this.currentPerson) {
        this.currentPersonSales = this.data_getMarket.data.sell_list.filter(x => x.name == this.currentPerson);
      }
      else {
        this.currentPersonSales = null;
      }

      // reset
      this.selectedSaleForCancel = null;
    },


    async getMarketForBuying(resource_type) {

      await this.getMarket(resource_type);

      this.data_getMarketForBuying = this.data_getMarket;

      // Add up all the quantities to get total number for sale
      var num_available = 0;
      for (let i = 0; i < this.data_getMarketForBuying.data.sell_list.length; i++) {
        num_available += this.data_getMarketForBuying.data.sell_list[i].amount;
      }

      // Get first price
      if (this.data_getMarketForBuying.data.sell_list.length > 0) {
        this.firstPrice = this.data_getMarketForBuying.data.sell_list[0].price;
      }
      else {
        this.firstPrice = null;
      }

      this.numAvailable = num_available;

      // reset
      this.buyQuantity = null;

    },


    async depositOrWithdraw() {

      try {
        const headers = { 'Content-Type': 'application/json' };


        var deposit_or_withdraw_str = ''
        if (this.adminDepositWithdraw == 'Deposit') {
          // add money
          deposit_or_withdraw_str = 'deposit';
        }
        else {
          // subract money
          deposit_or_withdraw_str = 'withdraw';
        }

        const body = { 'name': this.currentPerson,
                       'option': deposit_or_withdraw_str,
                       'dollars': this.adminMoney
                      };

        const response = await axios({
          method: 'post',
          url: 'http://127.0.0.1:5000/deposit_or_withdraw',
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
      this.getAssets(this.currentPerson);

    },


    async giveOrTakeResource() {

      try {
        const headers = { 'Content-Type': 'application/json' };


        var deposit_or_withdraw_str = ''
        if (this.adminDepositWithdrawResource == 'Deposit') {
          // add money
          deposit_or_withdraw_str = 'deposit';
        }
        else {
          // subract money
          deposit_or_withdraw_str = 'withdraw';
        }

        const body = { 'name': this.currentPerson,
                       'resource_type': this.adminSelectedResource,
                       'option': deposit_or_withdraw_str,
                       'amount': this.adminResourceAmount
                      };

        const response = await axios({
          method: 'post',
          url: 'http://127.0.0.1:5000/give_or_take_resource',
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

    },


    async newResource(resource_type) {

      try {
        const headers = { 'Content-Type': 'application/json' };

        const body = { 
                       'resource_type': String(resource_type)
                      };

        const response = await axios({
          method: 'post',
          url: 'http://127.0.0.1:5000/new_resource',
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
      this.getResources();

    },



    async debugFunc() {
      console.log('DEBUG A0')
    },

 


  },

};



</script>





<template>


  <body>





    <div class="flexbox-container-top">
      <div class="flexbox-item flexbox-item-4">

        <div v-if="sessionID">
          <p style="font-weight: bold;" class="relative text-xl text-center">Session ID: {{ sessionID }}</p>
        </div>
        <div v-else>
          <p class="relative text-xl text-center">Enter a new or existing Session ID</p>
        </div>

        <div style="text-align:center;">
          <InputText type="text" v-model="typingSessionID" placeholder="Session ID" style="text-align:center;" />
        </div>

        <div v-if="typingSessionID" style="text-align:center;">
          <Button style="width: 200px;" type="submit" severity="success" label="Submit" @click="setSessionID(typingSessionID)" rounded />
        </div>

      </div>
    </div>







    <div class="flexbox-container">
      <div class="flexbox-item flexbox-item-1">

        <div style="text-align:center;">
          <p style="display:inline-block;" class="relative text-3xl text-center">
            <i class="pi pi-user" style="font-size: 2.5rem"></i>
            Person
          </p>
        </div>
        <br>

        <div v-if="currentPerson">
          <p style="font-weight: bold;" class="relative text-xl text-center">Name: {{ currentPerson }}</p>
        </div>
        <div v-else>
          <p class="relative text-xl text-center">Select or create a person</p>
        </div>


        <SelectButton v-model="selectButtonPerson" @click="buttonSelectOrCreatePerson(selectButtonPerson)" :options="['Select person', 'Create person']" />


        <div v-if="selectPersonButton">

          <div v-if="data_getPeople">
            <Select v-model="selectedPerson" :options="data_getPeople.data.people" placeholder="Select person" class="w-full md:w-56" filter @update:modelValue="setCurrentPerson(selectedPerson)"/>
          </div>

        </div>




        <div v-if="createPersonButton" style="width: 100%">

          <InputText type="text" v-model="createdPerson" placeholder="Name" style="width: 100%;" />

          <div v-if="createdPerson">
            <Button style="width: 100%;" type="submit" severity="success" label="Submit" @click="createPerson(createdPerson)" rounded />
          </div>

        </div>



        <div v-if="money != null">
          <span style="font-weight: bold;" class="p-2 relative text-lg" >Money: &nbsp; ${{money.toFixed(2)}}</span>
        </div>

        <div v-if="currentPerson">
          <br><br>
          <div v-if="adminToggle">
            <ToggleSwitch v-model="adminToggle" />
            <span> &nbsp; &nbsp; Admin mode enabled </span>
          </div>
          <div v-else>
            <ToggleSwitch v-model="adminToggle" />
            <span> &nbsp; &nbsp; Admin mode disabled &nbsp; &nbsp; </span>
          </div>
        </div>

        <div v-if="adminToggle">

          <SelectButton v-model="adminSelectMoneyOrResorce" :options="['Money', 'Resource']" />

          <div v-if="adminSelectMoneyOrResorce == 'Money'">

            <InputNumber v-model="adminMoney" placeholder="Deposit or withdraw" inputId="currency-us" mode="currency" currency="USD" locale="en-US" fluid />

            <div v-if="adminMoney">
              <SelectButton v-model="adminDepositWithdraw" :options="['Deposit', 'Withdraw']" />
            </div>
            <div v-if="adminMoney && adminDepositWithdraw">
              <Button style="width: 100%;" type="submit" severity="success" label="Submit" @click="depositOrWithdraw" rounded />
            </div>

          </div>

          <div v-if="adminSelectMoneyOrResorce == 'Resource'">
            <SelectButton v-model="selectButtonResource" :options="['Select resource', 'Create resource']" />
          </div>

          <div v-if="adminSelectMoneyOrResorce == 'Resource' && selectButtonResource == 'Select resource' && data_getResources">

            <Select v-model="adminSelectedResource" :options="data_getResources.data.resources" placeholder="Select resource" class="w-full md:w-56" filter/>

            <div v-if="adminSelectedResource">

              <InputNumber v-model="adminResourceAmount" placeholder="Deposit or withdraw" inputId="integeronly" fluid />

              <div v-if="adminResourceAmount">
                <SelectButton v-model="adminDepositWithdrawResource" :options="['Deposit', 'Withdraw']" />
              </div>

              <div v-if="adminResourceAmount && adminDepositWithdrawResource">
                <Button style="width: 100%;" type="submit" severity="success" label="Submit" @click="giveOrTakeResource" rounded />
              </div>

            </div>

          </div>

          <div v-if="adminSelectMoneyOrResorce == 'Resource' && selectButtonResource == 'Create resource'">
            
            <InputText type="text" v-model="newResourceType" placeholder="Resource type" style="width: 100%;" />

            <div v-if="newResourceType">
              <Button style="width: 100%;" type="submit" severity="success" label="Submit" @click="newResource(newResourceType)" rounded />
            </div>

          </div>

        </div>





      </div>




      <div class="flexbox-item flexbox-item-2">

        <div style="text-align:center;">
          <p style="display:inline-block;" class="relative text-3xl text-center">
            <i class="pi pi-shop" style="font-size: 2.5rem"></i>
            Sell
          </p>
        </div>

        <br>


        <div v-if="data_getAssets">

          <DataTable selectionMode="single" v-model:selection="selectedResource" :value="data_getAssets.data.resource_list" size="small" scrollable scrollHeight="400px" tableStyle="min-width: 10rem" @row-select="getMarketForPerson(selectedResource.resource)" >
            <Column field="resource" header="Resource"></Column>
            <Column field="quantity" header="Quantity"></Column>
          </DataTable>

        </div>


        <div v-if="selectedResource">

          <p style="font-weight: bold;" class="relative text-xl text-center">{{selectedResource.resource}}</p>

            <InputNumber v-model="sellQuantity" inputId="integeronly" placeholder="Sell quantity" fluid :model-value="sellQuantity" @input="(e) => (sellQuantity = e.value)" />

            <InputNumber v-model="sellPrice" inputId="price_input" mode="currency" currency="USD" placeholder="Sell price" fluid :model-value="sellPrice" @input="(e) => (sellPrice = e.value)" />

            <div v-if="sellQuantity && sellPrice">
              <Button style="width: 100%;" type="submit" severity="success" label="Submit" @click="sell(currentPerson, selectedResource.resource, sellQuantity, sellPrice)" rounded />
            </div>

            <div v-if="currentPersonSales">
              <p class="relative text-xl text-center">Selling</p>

              <DataTable selectionMode="single" v-model:selection="selectedSaleForCancel" :value="currentPersonSales" size="small" scrollable scrollHeight="400px" tableStyle="min-width: 10rem" >
                <Column field="amount" header="Quantity"></Column>
                <Column field="price" header="Price"></Column>
              </DataTable>

              <div v-if="selectedSaleForCancel" >
                <Button style="width: 100%;" type="submit" severity="success" label="Cancel listing" @click="cancelSell(selectedSaleForCancel.sell_id)" rounded />
              </div>

            </div>

        </div>

        
        

      </div>



      <div class="flexbox-item flexbox-item-3">

        <div style="text-align:center;">
          <p style="display:inline-block;" class="relative text-3xl text-center">
            <i class="pi pi-shopping-bag" style="font-size: 2.5rem"></i>
            Buy
          </p>
        </div>
        <br>

        <div v-if="currentResource">
          <p style="font-weight: bold;" class="relative text-xl text-center">Resource: {{ currentResource }}</p>
        </div>
        <div v-else>
          <p class="relative text-xl text-center">Select a resource</p>
        </div>

        <div v-if="data_getResources">
          <Select v-model="currentResource" :options="data_getResources.data.resources" placeholder="Select resource" class="w-full md:w-56" filter @update:modelValue="getMarketForBuying(currentResource)"/>
        </div>

        <div v-if="currentResource && data_getMarketForBuying">

          <div v-if="firstPrice">
            <p class="relative text-xl text-center">Available: {{numAvailable}} &nbsp; &nbsp; &nbsp; Price: ${{firstPrice.toFixed(2)}}</p>
          </div>
          <div v-else>
            <p class="relative text-xl text-center">Available: {{numAvailable}}</p>
          </div>

          <div v-if="currentPerson">

            <InputNumber v-model="buyQuantity" inputId="integeronly" placeholder="Buy quantity" fluid @update:modelValue="getPrice(currentResource, buyQuantity)" />

            <div v-if="buyQuantity && data_getPrice && data_getPrice.data.price">
              <span class="p-2 relative text-lg" >Total Price: &nbsp; ${{data_getPrice.data.price.toFixed(2)}} &nbsp; &nbsp; Unit Price &nbsp; ${{pricePerUnit}}</span>

              <div v-if="(money != null) && (money >= data_getPrice.data.price)">
                <Button style="width: 100%;" type="submit" severity="success" label="Submit" @click="buy(currentPerson, currentResource, buyQuantity)" rounded />
              </div>

            </div>

          </div>


        </div>

      </div>



    </div>






    <!-- <div class="flexbox-container-bottom">
      <div class="flexbox-item flexbox-item-5">

        <Button type="submit" severity="success" label="Get Market" @click="getMarket('apple')" rounded />
          <div v-if="data_getMarket">
            <pre>    {{ data_getMarket.message }}</pre>
          </div>
          <div v-else><br></div>


          <Button type="submit" severity="success" label="Get Price" @click="getPrice('apple', 1)" rounded />
          <div v-if="data_getPrice">
            <pre>    {{ data_getPrice.message }}</pre>
          </div>
          <div v-else><br></div>


          <Button type="submit" severity="success" label="Get Assets" @click="getAssets('Phillip Geeter')" rounded />
          <div v-if="data_getAssets">
            <pre>    {{ data_getAssets.message }}</pre>
          </div>
          <div v-else><br></div>


          <Button type="submit" severity="success" label="Get People" @click="getPeople" rounded />
          <div v-if="data_getPeople">
            <pre>    {{ data_getPeople.message }}</pre>
          </div>
          <div v-else><br></div>


          <Button type="submit" severity="success" label="Create Person" @click="createPerson('Phillip Geeter')" rounded />
          <div v-if="data_createPerson">
            <pre>    {{ data_createPerson.message }}</pre>
          </div>
          <div v-else><br></div>


          <Button type="submit" severity="success" label="Sell" @click="sell('Phillip Geeter', 'apple', 2, 8)" rounded />
          <div v-if="data_sell">
            <pre>    {{ data_sell.message }}</pre>
          </div>
          <div v-else><br></div>


          <Button type="submit" severity="success" label="Buy" @click="buy('Phillip Geeter', 'apple', 2)" rounded />
          <div v-if="data_buy">
            <pre>    {{ data_buy.message }}</pre>
          </div>
          <div v-else><br></div>


      </div>
    </div> -->




  </body>


  
</template>



<style scoped>


.flexbox-container-top {
  display: flex;
  justify-content: space-around;
  height: 20vh;
  width: 90vw;
}

.flexbox-container-bottom {
  display: flex;
  justify-content: space-around;
  height: 65vh;
  width: 90vw;
}

.flexbox-container {
  display: flex;
  justify-content: space-around;
  height: 80vh;
  width: 90vw;
}

.flexbox-item {
  width: 300px;
  margin: 8px;
  border: 3px solid #333;
  background-color: #dfdfdf;
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




</style>
